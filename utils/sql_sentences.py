# 获取Sidus用户信息
SQL_User_info = """
    select A.first_name ,A.last_name,B.icon_file as sidus_avatar from sidusdb.tb_user as A left join sidusdb.tb_icon as B on A.id=B.fk_user_id where A.id = %s order by B.id desc limit 1;
"""

SQL_User_Get = """
    select * from sidusdb.tb_user where email= %s;
"""

SQL_User_Insert = """
    insert into sidusdb.tb_user(id,email,phone_number,first_name,last_name,password,occupation,register_time,login_time,gender,email_show,city,camera_model,lighting_model,software_model,computer_model,company,website,age,begin_job_time,state,registration_id,fk_vip_level,mobile_model,sys,lat,lng) values(0,%(email)s,%(phone_number)s,%(first_name)s,%(last_name)s,%(password)s,%(occupation)s,%(register_time)s,%(login_time)s,%(gender)s,%(email_show)s,%(city)s,%(camera_model)s,%(lighting_model)s,%(software_model)s,%(computer_model)s,%(company)s,%(website)s,%(age)s,%(begin_job_time)s,%(state)s,%(registration_id)s,%(fk_vip_level)s,%(mobile_model)s,%(sys)s,%(lat)s,%(lng)s);
"""

"""
*******************Product SQL********************
"""
"""
*******Client SQL**********
"""
# Client获取Sidus hardware all product
SQL_Hardware_All_Product_Client = """
    select id,uuid_ascii_code as uuid,product_name,product_status,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date,offered_by from sidusdb.tb_hardware_product where product_display=1 and offered_by in %s;
"""

# Client获取Sidus hardware product offered
SQL_Hardware_Product_Client = """
    select id,uuid_ascii_code as uuid,product_name,product_status,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date,offered_by from sidusdb.tb_hardware_product where product_display =1 and product_status=1 and offered_by = %s ;
"""

# Client 获取Sidus hardware product by uuid
SQL_Hardware_Product_UUID_Client = """
    select uuid_ascii_code as uuid,product_name,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date,offered_by from sidusdb.tb_hardware_product where product_display=1 and uuid_ascii_code=%s;
"""

# Client获取 Sidus hardware product  series
SQL_Hardware_Product_Series_Client = """
    select distinct(product_series),product_name as sub_product,uuid_ascii_code as uuid,offered_by from sidusdb.tb_hardware_product where product_display =1 and product_status=1 and offered_by in %s;
"""

# Client获取 Sidus hardware product  series
SQL_Hardware_Product_SubPro_Client = """
    select product_name as sub_product,uuid_ascii_code as uuid from sidusdb.tb_hardware_product where product_display =1 and offered_by=%s and product_status=1 and product_series=%s;
"""

# Client获取 Sidus hardware product series offered
SQL_Hardware_Product_offered_series_Client = """
    select id,uuid_ascii_code as uuid,product_name,product_status,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date,offered_by from sidusdb.tb_hardware_product where product_display =1 and offered_by = %s and product_status=1 and product_series=%s;
"""

"""
*******Admin SQL**********
"""

# 插入Sidus hardware firmware product数据
SQL_Insert_Firware_Product = """
    insert into sidusdb.tb_hardware_product(id,product_status,product_display,product_released_date,product_updated_time,product_updates_downloads_requests,product_updates_downloads,uuid_ascii_code,product_project_num,product_name,product_series,offered_by,product_updated_admin_name) values (0,%(product_status)s,1,current_date(),current_date(),0,0,%(uuid_ascii_code)s,%(product_project_num)s,%(product_name)s,%(product_series)s,%(offered_by)s,%(product_updated_admin_name)s);
"""

# 查询是否有 Sidus hardware firmware product数据
SQL_Firware_Product_Count = """
    select count(id) as count from sidusdb.tb_hardware_product where uuid_ascii_code=%s;
"""

SQL_Firware_Product_Count_By_Id = """
    select count(*) as count from sidusdb.tb_hardware_product where id=%s;
"""

# 更新Sidus hardware firmware product数据
SQL_Updatet_Firware_Product = """
    update sidusdb.tb_hardware_product set product_updated_time=current_date(),product_series=%(product_series)s,offered_by=%(offered_by)s,product_updated_admin_name=%(product_updated_admin_name)s,product_project_num = %(product_project_num)s,product_name=%(product_name)s,uuid_ascii_code=%(uuid_ascii_code)s where id=%(id)s;
"""
# 删除Sidus hardware firmware product数据
SQL_Delete_Firware_Product = """
    delete from sidusdb.tb_hardware_product where uuid_ascii_code=%s;
"""

# 更新产品隐藏状态
SQL_Display_Firware_Product = """
    update sidusdb.tb_hardware_product set product_display = abs(product_display -1) where id=%s;
"""

# 更新产品使用状态
SQL_Status_Firware_Product = """
    update sidusdb.tb_hardware_product set product_status = abs(product_status - 1) where uuid_ascii_code=%s and id>0;
"""

# 更新产品使用状态
SQL_Status_Product = """
    update sidusdb.tb_hardware_product set product_status = 1 where uuid_ascii_code=%s and id>0;
"""
# 更新产品最后更新人
SQL_Status_Product_Admin = """
    update sidusdb.tb_hardware_product set product_updated_admin_name = %s where uuid_ascii_code=%s and id>0;
"""

# 获取Sidus hardware all product
SQL_Hardware_All_Product = """
    select id,uuid_ascii_code as uuid,product_name,product_status,product_display,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date,offered_by from sidusdb.tb_hardware_product;
    """

SQL_Hardware_Product_UUID = """
    select uuid_ascii_code as uuid,product_name,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date,offered_by from sidusdb.tb_hardware_product where uuid_ascii_code=%s;
"""

SQL_Hardware_Product_INFO_BY_UUID = """
   select * from sidusdb.tb_hardware_product where uuid_ascii_code=%s;
"""

# 获取Sidus hardware product offered
SQL_Hardware_Product = """
    select id,uuid_ascii_code as uuid,product_name,product_status,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date,offered_by from sidusdb.tb_hardware_product where offered_by = %s ;
"""
# 获取 Sidus
SQL_Hardware_Product_Series = """
    select distinct(product_series),product_name as sub_product,uuid_ascii_code as uuid,offered_by from sidusdb.tb_hardware_product where offered_by in %s;
"""

# Client获取 Sidus harsware product series offered
SQL_Hardware_Product_offered_series = """
    select id,uuid_ascii_code as uuid,product_name,product_status,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date,offered_by from sidusdb.tb_hardware_product where offered_by = %s and product_series=%s;
"""

# 获取已创建的产品
# 获取Sidus hardware all product
SQL_Created_Hardware_All_Product = """
    select id,uuid_ascii_code as uuid,product_name,product_display,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date,offered_by from sidusdb.tb_hardware_product where product_status=1;
    """
# 获取Sidus hardware product offered
SQL_Created_Hardware_Product = """
    select id,uuid_ascii_code as uuid,product_name,product_status,product_display,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date,offered_by from sidusdb.tb_hardware_product where offered_by = %s and product_status=1;
"""

# 获取 Sidus harsware product  series
SQL_Created_Hardware_Product_Series = """
    select distinct(product_series),offered_by from sidusdb.tb_hardware_product where offered_by in %s and product_status=1;
"""
# 获取 Sidus harsware product series offered
SQL_Created_Hardware_Product_offered_series = """
    select id,uuid_ascii_code as uuid,product_name,product_status,product_display,product_series,product_project_num as prj_name,product_updated_admin_name as admin_name,product_released_date as c_date,product_updated_time as up_date from sidusdb.tb_hardware_product where offered_by = %s and product_series=%s and product_status=1;
"""

"""
*******************固件SQL********************
"""
"""
*******Client SQL**********
"""
# Client获取Sidus hardware firmware
SQL_Hardware_avail_Firmware_Client = """
    select id,firmware_type,firmware_normal,hardware_version,firmware_version,firmware_version_built_in,firmware_environment,firmware_available,firmware_detail_cns,firmware_detail_cnt,firmware_detail_en ,firmware_released_date,firmware_updated_time from sidusdb.tb_hardware_firmware where firmware_display=1 and firmware_available=1 and uuid_ascii_code = %s;
"""

SQL_Hardware_Unavail_Firmware_Client = """
    select id,firmware_type,firmware_normal,hardware_version,firmware_version,firmware_version_built_in,firmware_environment,firmware_available,firmware_detail_cns,firmware_detail_cnt,firmware_detail_en ,firmware_released_date,firmware_updated_time from sidusdb.tb_hardware_firmware where firmware_display=1 and uuid_ascii_code = %s and hardware_version = %s and firmware_type = %s and firmware_available = 0;
"""

SQL_Hardware_Unavail_Ble_Firmware_Client = """
    select distinct(hardware_version) from sidusdb.tb_hardware_firmware where firmware_display=1 and uuid_ascii_code =%s and firmware_type ='Ble';
"""

SQL_Hardware_Firmware_Blue_Client_Version = """
 select uuid_ascii_code,firmware_type,hardware_version,firmware_version_built_in,firmware_version,firmware_normal,firmware_environment,firmware_available,firmware_detail_en,firmware_detail_cns,firmware_detail_cnt ,firmware_released_date,firmware_updated_time from sidusdb.tb_hardware_firmware where uuid_ascii_code = 'normal' and firmware_type='Ble' and firmware_available=1 and firmware_normal=1 and firmware_display = 1 and hardware_version=%s;
"""

SQL_Hardware_Firmware_Blue_Hardware_Client = """
 select * from sidusdb.tb_hardware_firmware where uuid_ascii_code = 'normal' and firmware_type='Ble' and firmware_available=1 and firmware_normal=1 and firmware_display = 1 and hardware_version = %s;
"""

# 获取激活蓝牙信息
SQL_Hardware_Firmware_Blue_Client = """
 select * from sidusdb.tb_hardware_firmware where uuid_ascii_code = 'normal' and firmware_type='Ble' and firmware_available=1 and firmware_normal=1 and firmware_display = 1;
"""

"""
*******Admin SQL**********
"""
SQL_Hardware_Firmware = """
    select id,firmware_type,firmware_available,firmware_status,hardware_version,firmware_version,firmware_display,firmware_normal,firmware_version_built_in,firmware_environment,firmware_detail_cns,firmware_detail_cnt,firmware_detail_en ,firmware_released_date,firmware_updated_time from sidusdb.tb_hardware_firmware where firmware_available=1 and uuid_ascii_code = %s;   
"""
SQL_Hardware_Unavail_Firmware = """
    select id,firmware_type,firmware_available,firmware_status,hardware_version,firmware_version,firmware_display,firmware_normal,firmware_version_built_in,firmware_environment,firmware_detail_cns,firmware_detail_cnt,firmware_detail_en from sidusdb.tb_hardware_firmware where firmware_available=0 and uuid_ascii_code = %s and hardware_version = %s and firmware_type = %s;
"""
SQL_Hardware_Unavail_Ble_Firmware = """
    select distinct(hardware_version) from sidusdb.tb_hardware_firmware where uuid_ascii_code =%s and firmware_type = 'Ble';
"""

SQL_Hardware_Firmware_ID = """
    select * from sidusdb.tb_hardware_firmware where id = %s;
"""

# 删除固件信息
SQL_Delete_Firware_UUID = """
    delete from sidusdb.tb_hardware_firmware where uuid_ascii_code=%s;
"""

# 删除指定固件信息
SQL_Delete_Firware_ID = """
    delete from sidusdb.tb_hardware_firmware where id=%s;
"""
# 删除指定hardware_version的固件信息
SQL_Delete_Firware_Hardware_Version = """
   delete from  sidusdb.tb_hardware_firmware where uuid_ascii_code=%s and firmware_type=%s and hardware_version=%s;
"""

# 更新固件不显示
SQL_Display_Firware = """
    update sidusdb.tb_hardware_firmware set firmware_display = abs(firmware_display -1) where id=%s;
"""
# 上传固件信息
SQL_Insert_Hardware_Firmware = """
    insert into sidusdb.tb_hardware_firmware(id,firmware_status,uuid_ascii_code,firmware_type,firmware_normal,hardware_version,firmware_version_built_in,firmware_version,firmware_url,firmware_size,firmware_environment,firmware_released_date,firmware_updated_time,firmware_available,firmware_display,firmware_detail_en,firmware_detail_cns,firmware_detail_cnt,firmware_updated_admin_name) values (0,%(firmware_status)s,%(uuid_ascii_code)s,%(firmware_type)s,%(firmware_normal)s,%(hardware_version)s,%(firmware_version_built_in)s,%(firmware_version)s,%(firmware_url)s,%(firmware_size)s,%(firmware_environment)s,current_date(),current_date(),1,1,%(firmware_detail_en)s,%(firmware_detail_cns)s,%(firmware_detail_cnt)s,%(firmware_updated_admin_name)s);
"""

# 更新固件是否为正式版本
SQL_Update_Hardware_Firmware_Status = """
    update sidusdb.tb_hardware_firmware set firmware_status = 1 where id = %s; 
"""

SQL_Update_Hardware_Disable_Firmware_Status = """
    update sidusdb.tb_hardware_firmware set firmware_status = 0 where uuid_ascii_code=%s and firmware_type=%s and hardware_version=%s and firmware_version=%s and id >0;
"""
# 更新固件的激活状态
SQL_Update_Hardware_Firmware_available = """
    update sidusdb.tb_hardware_firmware set firmware_available = 0 where uuid_ascii_code=%s and firmware_type=%s and hardware_version=%s and id >0; 
"""

# 更新通用蓝牙固件的激活状态
SQL_Update_Hardware_Firmware_normal_available = """
    update sidusdb.tb_hardware_firmware set firmware_available = 0 where firmware_type='Ble' and firmware_normal=1 and id >0 and hardware_version = %s; 
"""

# 更新固件的激活状态
SQL_Update_Hardware_Firmware_able = """
    update sidusdb.tb_hardware_firmware set firmware_available = 1 where id = %s; 
"""

# 查询当前的固件是否存在
SQL_Update_Hardware_Firmware_Exist = """
    select id,count(id) as count from sidusdb.tb_hardware_firmware where uuid_ascii_code = %s and firmware_type=%s and hardware_version=%s and firmware_version=%s;
"""

# 获取所有通用蓝牙信息
SQL_Hardware_Firmware_Blue = """
 select * from sidusdb.tb_hardware_firmware where uuid_ascii_code = 'normal' and firmware_type='Ble' and firmware_normal=1 and firmware_available=1;
"""

SQL_Hardware_Firmware_Blue_Version = """
 select uuid_ascii_code,firmware_type,hardware_version,firmware_version_built_in,firmware_version,firmware_normal,firmware_environment,firmware_available,firmware_detail_en,firmware_detail_cns,firmware_detail_cnt  ,firmware_released_date,firmware_updated_time from sidusdb.tb_hardware_firmware where uuid_ascii_code = 'normal' and firmware_type='Ble' and firmware_available=1 and firmware_normal=1 and hardware_version=%s;
"""

# 更新固件不带文件信息
SQL_Update_Hardware_Firmware_without_file = """
     update sidusdb.tb_hardware_firmware set firmware_version=%(firmware_version)s,firmware_version_built_in = %(firmware_version_built_in)s,firmware_environment=%(firmware_environment)s,firmware_detail_en=%(firmware_detail_en)s,firmware_detail_cns=%(firmware_detail_cns)s,firmware_detail_cnt=%(firmware_detail_cnt)s,firmware_updated_admin_name=%(firmware_updated_admin_name)s where id = %(id)s;
"""

# 更新固件带文件信息
SQL_Update_Hardware_Firmware_with_file = """
    update sidusdb.tb_hardware_firmware set firmware_version=%(firmware_version)s,firmware_version_built_in = %(firmware_version_built_in)s ,firmware_environment = %(firmware_environment)s,firmware_detail_en=%(firmware_detail_en)s,firmware_detail_cns=%(firmware_detail_cns)s,firmware_detail_cnt=%(firmware_detail_cnt)s,firmware_updated_admin_name=%(firmware_updated_admin_name)s, firmware_url = %(firmware_url)s,firmware_size=%(firmware_size)s where id = %(id)s;
"""
# 更新固件所有信息
SQL_Update_Hardware_Firmware = """
    update sidusdb.tb_hardware_firmware set firmware_version=%(firmware_version)s,firmware_version_built_in = %(firmware_version_built_in)s,firmware_environment = 1,firmware_detail_en=%(firmware_detail_en)s,firmware_detail_cns=%(firmware_detail_cns)s,firmware_detail_cnt=%(firmware_detail_cnt)s,firmware_updated_admin_name=%(firmware_updated_admin_name)s, firmware_url = %(firmware_url)s,firmware_size=%(firmware_size)s,firmware_released_date=%(firmware_released_date)s,firmware_updated_time=current_date(),firmware_available=1,firmware_display=1,firmware_normal=%(firmware_normal)s,firmware_status=1 where id = %(id)s;
"""

# 通用蓝牙更新
SQL_Update_Hardware_Firmware_Normal_Ble = """
    update sidusdb.tb_hardware_firmware set firmware_version_built_in = %(firmware_version_built_in)s,firmware_environment = %(firmware_environment)s,firmware_detail_en=%(firmware_detail_en)s,firmware_detail_cns=%(firmware_detail_cns)s,firmware_detail_cnt=%(firmware_detail_cnt)s,firmware_updated_admin_name=%(firmware_updated_admin_name)s, firmware_url=%(firmware_url)s,firmware_status = %(firmware_status)s,firmware_size=%(firmware_size)s where firmware_type='Ble' and firmware_normal =1 and firmware_available=1 and firmware_version = %(firmware_version)s and hardware_version=%(hardware_version)s;
"""

"""
*******************Search SQL********************
"""
"""Client Search"""
# 用户产品搜索
SQL_Hardware_Product_Search_Client = """
    SELECT id,uuid_ascii_code,product_project_num,product_name,product_series,offered_by, product_updated_admin_name,product_released_date,product_updated_time FROM sidusdb.tb_hardware_product where uuid_ascii_code like '%{}%' or product_name like '%{}%' or product_series like '%{}%' or product_project_num like '%{}%' and product_display=1;
"""

"""Admin 产品搜索"""
SQL_Hardware_Product_Search = """
    SELECT * FROM sidusdb.tb_hardware_product where uuid_ascii_code like '%{}%' or product_name like '%{}%' or product_series like '%{}%' or product_project_num like '%{}%' and offered_by in %s;
"""

"""Admin 部门搜索"""
SQL_Hardware_Department_Search = """
    SELECT * FROM iot.tb_department where department_name like '%{}%';
"""

"""Admin 用户搜索"""
SQL_Hardware_User_Search = """
    SELECT * FROM iot.tb_users where first_name like '%{}%';
"""

"""获取用户的城市地理信息"""
SQL_User_Country = """
    select id as sidus_id,first_name,date_format(register_time,"%Y-%m-%d") as register_date,city,lat,lng,sys from sidusdb.tb_user where city is not null and lat is not null and (city != "" or lat != "");
"""

"""
*******************SQL Function********************
"""

"""LOCAL"""
SQL_IOT_COUNTRY = """
insert into iot.sidus_country values(0,%(sidus_id)s,%(first_name)s,%(register_date)s,%(city)s,%(lat)s,%(lng)s,%(country)s,%(sys)s);
"""

