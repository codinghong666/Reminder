import re, hashlib, json, httpx, uuid, time
from uniform_login_des import strEnc
from datetime import datetime, timezone


def login(sduid: str, password: str,
          fingerprint: str | None = str(uuid.uuid4()), max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return _perform_login(sduid, password, fingerprint)
        except SystemError as e:
            if "HTML错误页面" in str(e) or "服务器返回无效响应" in str(e):
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 递增等待时间
                    print(f"登录失败，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print("重试次数已达上限，登录失败。")
                    raise
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"登录过程中出现错误: {str(e)}")
                print(f"{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                raise
    
    raise SystemError("登录失败，已达到最大重试次数")


def _perform_login(sduid: str, password: str, fingerprint: str):
    page = httpx.get(
        "https://pass.sdu.edu.cn/cas/login",
        params={
            "service": "https://aiassist.sdu.edu.cn/common/actionCasLogin?redirect_url=https%3A%2F%2Faiassist.sdu.edu.cn%2Fpage%2Fsite%2FnewPc%3Flogin_return%3Dtrue"})
    lt = re.findall(r'"lt" value="(.*?)"', page.text)[0]
    rsa = strEnc(sduid + password + lt, "1", "2", "3")
    execution = re.findall('"execution" value="(.*?)"', page.text)[0]
    event_id = re.findall('"_eventId" value="(.*?)"', page.text)[0]
    murmur_s = hashlib.sha256(fingerprint.encode()).hexdigest()
    device_status = httpx.post(
        "https://pass.sdu.edu.cn/cas/device",
        data={
            "u": strEnc(sduid, "1", "2", "3"),
            "p": strEnc(password, "1", "2", "3"),
            "m": "1",  # mode 1 to get if device registered
            "d": fingerprint, "d_s": murmur_s,
            "d_md5": hashlib.md5(murmur_s.encode()).hexdigest(),  # md5 of d_s
        }, cookies=page.cookies)
    device_status_dict = json.loads(device_status.text)
    match device_status_dict.get("info"):
        case "binded" | "pass":
            pass
        case "bind":
            phone_number = device_status_dict.get("m", "")
            print(f"需要手机验证码登录")
            print(f"手机号码: {phone_number}")
            print("正在发送验证码...")
            tmp = httpx.post(
                "https://pass.sdu.edu.cn/cas/device",
                data={"m": "2"}, cookies=page.cookies)
            
            # 检查响应是否为HTML错误页面
            if tmp.text.strip().startswith('<html>') or tmp.text.strip().startswith('<!DOCTYPE'):
                print("服务器返回错误页面，可能是网络问题或服务器繁忙。")
                print("请稍后重试，或检查网络连接。")
                raise SystemError("服务器返回HTML错误页面，请稍后重试")
            
            # 尝试解析JSON响应
            try:
                sms_response = json.loads(tmp.text)
                if sms_response.get("info") == "send":
                    print("✓ 验证码已发送到手机")
                    print(f"请查看手机 {phone_number} 收到的短信验证码")
                else:
                    raise SystemError(f"Unknown SMS status: {tmp.text}")
            except json.JSONDecodeError:
                print(f"服务器返回非JSON响应: {tmp.text[:200]}...")
                raise SystemError(f"服务器返回无效响应: {tmp.text[:100]}")
            
            print("\n" + "="*50)
            print("请输入验证码")
            print("="*50)
            verification_code = input("验证码: ")
            remember_device = input("记住此设备，下次登录免验证？(y/N): ").lower() == 'y'
            
            body = {
                "d": murmur_s, "i": fingerprint, "m": "3", "u": sduid,
                "c": verification_code, "s": "1" if remember_device else "0"}
            k = httpx.post("https://pass.sdu.edu.cn/cas/device",
                           data=body, cookies=page.cookies)
            while k.text == '{"info":"codeErr"}':
                print("\n❌ 验证码错误，请重新输入")
                body["c"] = input("验证码: ")
                k = httpx.post("https://pass.sdu.edu.cn/cas/device",
                               data=body, cookies=page.cookies)
            if k.text == '{"info":"ok"}':
                print("\n✅ 登录成功！")
                if body["s"] == "1":
                    print(f"设备已记住，设备指纹: {fingerprint}")
                    print("下次登录将不再需要验证码")
        case _:
            print(
                "Please check your username. Device information cannot be loaded by SDU pass.")
            raise SystemError(
                "Unknown device status: {}".format(str(device_status_dict)))
    page = httpx.post(
        "https://pass.sdu.edu.cn/cas/login", cookies=page.cookies, params={
            "service": "https://aiassist.sdu.edu.cn/common/actionCasLogin?redirect_url=https%3A%2F%2Faiassist.sdu.edu.cn%2Fpage%2Fsite%2FnewPc%3Flogin_return%3Dtrue"},
        data={"rsa": rsa, "ul": len(sduid), "pl": len(password), "lt": lt,
              "execution": execution, "_eventId": event_id})
    page = httpx.get(page.headers["location"])
    header = str(page.headers)
    where = header.find("expires=") + 8
    expires = (datetime.strptime(
        header[where:where + 29], "%a, %d-%b-%Y %H:%M:%S GMT")
               .replace(tzinfo=timezone.utc))
    return {
        "cookies": {cookie: value for cookie, value in page.cookies.items()},
        "expires": expires}
