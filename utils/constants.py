# 常量设置

class RET:
    OK = "200"
    METHODERR = "4001"
    PARAMLOST = "4002"
    PARAMERR = "4003"
    DBERR = "4004"
    NODATA = "4005"
    DATAEXIST = "4006"
    DATAERR = "4007"

    USERLOCKED = "4100"
    USERUNRGT = "4101"
    PWDERR = "4102"
    USERERR = "4103"
    USERRGTED = "4104"
    ROLEERR = "4105"
    ROLENOTEXIST = "4106"
    ROLEPEMIT = "4107"
    VERIFYCODEERR = "4108"

    USERUNLOG = "4110"
    SESSIONERR = "4111"
    LOGINERR = "4112"
    DEPARTMENTNOTEXIST = '4113'

    PWDTYPEERR = '4122'
    PWDCOMMITERR = '4123'

    REQERR = "4201"
    IPERR = "4202"
    THIRDERR = "4301"
    IOERR = "4302"
    FILEUPLOADERR = "4303"

    PORDUCTEXIST = "4401"
    PORDUCTNOTEXIST = "4402"
    FIRMWAREXIST = "4403"
    FIRMWARNOTEXIST = "4404"

    SERVERERR = "4500"
    UNKOWNERR = "4501"


Info_Map = {
    RET.OK: u"成功",
    RET.METHODERR: u'请求方法错误',
    RET.PARAMLOST: u'请求参数缺失',
    RET.DBERR: u"数据库查询错误",
    RET.NODATA: u"无Token数据",
    RET.DATAEXIST: u"数据已存在",
    RET.DATAERR: u"数据错误",

    RET.SESSIONERR: u"用户验证失败",
    RET.LOGINERR: u"用户登录失效",
    RET.PARAMERR: u"请求参数错误",
    RET.USERLOCKED: u"用户被锁定",
    RET.USERERR: u"用户不存在或未激活",
    RET.USERUNLOG: u"用户未登录",
    RET.ROLEERR: u"用户角色错误",
    RET.ROLENOTEXIST: u"用户角色不存在",
    RET.ROLEPEMIT: u"用户角色权限限制",
    RET.PWDERR: u"密码错误",
    RET.PWDTYPEERR: u"密码格式错误",
    RET.PWDCOMMITERR: u"验证密码不一致",
    RET.VERIFYCODEERR: u"验证码错误或过期",

    RET.DEPARTMENTNOTEXIST: u'部门不存在',

    RET.REQERR: u"非法请求或请求次数受限",
    RET.IPERR: u"IP受限",
    RET.THIRDERR: u"第三方系统错误",
    RET.FILEUPLOADERR: u"文件上传失败",
    RET.PORDUCTEXIST: u"产品已存在",
    RET.PORDUCTNOTEXIST: u"产品已存在",
    RET.FIRMWAREXIST: "固件已存在",
    RET.FIRMWARNOTEXIST: "固件不存在",

    RET.IOERR: u"文件读写错误",
    RET.SERVERERR: u"内部错误",
    RET.UNKOWNERR: u"未知错误",
}

# base_ip = "54.176.83.64"
base_ip = "127.0.0.1"
# S3 的头地址
S3_image_url = 'https://d8ao2pdw51vzz.cloudfront.net/'
# S3文件上传
S3_upload_url = 'http://127.0.0.1:8000/upload/upload_single_file/'

# Sidus登录网址
Sidus_Pro_LoginUrl = 'http://127.0.0.1:8000/account/login/'

# Sidus注册邮箱网址
Sidus_Pro_ReEmailUrl = 'http://127.0.0.1:8000/account/get_register_code/'

# Sidus 校验邮箱
Sidus_Pro_Veridy_Reg = 'http://127.0.0.1:8000/account/verify_register_code/'

# Sidus注册网址
Sidus_Pro_RegisterUrl = 'http://127.0.0.1:8000/account/register/'

# Sidus上传固件信息
Sidus_Pro_ProductUrl = 'http://127.0.0.1:8000/product/hardware_firmware/'

# Sidus上传固件产品信息
Sidus_Pro_FirmWareProductUrl = 'http://127.0.0.1:8000/product/hardware_product/'

# Sidus上传头像
Sidus_Pro_Post_avatar = 'http://127.0.0.1:8000/user/upload_icon/'

# Sidus更新用户信息
Sidus_Pro_Post_User_info = 'http://127.0.0.1:8000/account/edit/'

# Sidus 更新密码
Sidus_Pro_ChangePWD = 'http://127.0.0.1:8000/account/modify_password/'

# Sidus 获取密码验证邮箱
Sidus_Pro_ChangePWDEmail = 'http://127.0.0.1:8000/account/get_modify_password_code/'

# Sidus 邮箱登录获取验证码
Sidus_Pro_EmailLogin = 'http://127.0.0.1:8000/account/get_login_code/'

# SidusDev登录网址
Sidus_Dev_LoginUrl = 'http://54.153.48.226:8000/account/login/'
# Dev Sidus上传固件信息
Sidus_Dev_FirmWareUrl = 'http://54.153.48.226:8000/product/hardware_firmware/'
# Dev Sidus上传固件信息
Sidus_Dev_FirmWareProductUrl = 'http://54.153.48.226:8000/product/hardware_product/'

# 删除测试服账号
Sidus_Dev_Delete_User = 'http://54.153.48.226:8000/account/account_view/?email={}'

# Sidus Product database
Sidus_Pro_Database = {
    'host': '13.56.206.193',
    'port': 3306,
    'user': 'ota',
    'password': 'Sidus&futurelab',
    'database': 'sidusdb',
    'tag': 'pro'
}

# Sidus Dev database
Sidus_Dev_Database = {
    'host': '13.52.13.18',
    'port': 3306,
    'user': 'sidus',
    'password': 'Sidus&futurelab',
    'database': 'sidusdb',
    'tag': 'dev'
}

# Local database
Local_Database_Sidus = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'sidusdb'
}

# Local database
Local_Database_Iot = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '12345678',
    'database': 'iot'
}
