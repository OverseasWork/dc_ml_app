# -*- coding: utf-8 -*-
# @Time    : 2022/9/29 00:06
# @Author  : HuangSir
# @FileName: req_sql.py
# @Software: PyCharm
# @Desc: 查询语句

import sys

sys.path.append('..')
import warnings

warnings.filterwarnings('ignore')


class QuerySql:
    '''查询语句'''

    def base_sql(self, customer_id, loan_app_id):
        sql = f"""select
                a.customer_id ,
                a.loan_app_id ,
                a.marital_status,
                extract(year FROM age(a.create_time,a.ktp_date_of_birth)) AS age,
                a.last_education ,
                a.children_number ,
                c.profession_id  ,
                c.industry_id ,
                c.working_years,
                c.job_type,
                c.salary 
                FROM 
                t_personal_info a 
                INNER JOIN 
                t_employment c 
                ON a.customer_id = c.customer_id and a.loan_app_id = c.loan_app_id
                WHERE a.customer_id = '{customer_id}' and a.loan_app_id = '{loan_app_id}'
                limit 1
        """
        return sql

    def equip_sql(self, customer_id, loan_app_id):
        sql = f"""select
                aa.*
                FROM
                (SELECT 
                a.customer_id,
                a.id as loan_app_id,
                x.device_brand ,--AS "设备品牌",
                x.system_version ,--AS "安卓版本号",
                x.remaining_battery ,--AS "剩余电量",
                round(x.remaining_memory::NUMERIC /(1024*1024*1024),2) AS  remaining_memory,--AS "可用内存",
                round(x.total_memory::NUMERIC/(1024*1024*1024),2) AS total_memory,--AS "总内存",
                round(x.remaining_storage_space::NUMERIC/(1024*1024*1024),2) AS remaining_storage_space,--AS "剩余存储空间",
                round(x.total_storage_space::NUMERIC/(1024*1024*1024),2) AS total_storage_space,--AS "总存储空间",
                
                ROUND(ABS(EXTRACT(EPOCH FROM a.create_time - x.installation_time))/3600) install_apply_seconds  ,--AS "安装到下单时差",
                x.length ,--AS "屏幕长度",
                row_number() over(PARTITION by x.mobile  order by x.installation_time DESC) as rn
                FROM
                t_loan_app a
                INNER JOIN
                t_customer c ON a.customer_id = c.id
                LEFT JOIN
                x_equipment x ON x.mobile = c.mobile 
                AND x.installation_time IS NOT NULL
                AND x.create_time <= a.create_time
                WHERE 
                a.customer_id = '{customer_id}'
                AND
                a.id = '{loan_app_id}'
                ) aa 
                WHERE aa.rn = 1
        """
        return sql

    def lbs_sql(self, customer_id, loan_app_id):
        sql = f"""SELECT 
                t.*
                FROM 
                (SELECT 
                t2.id as loan_app_id,
                t1.customer_id,
                t1.state,
                t1.city,
                row_number() over(PARTITION by t1.customer_id  order by t1.create_time DESC) as rn
                FROM t_record_location_conversion t1 INNER JOIN t_loan_app t2 ON t1.customer_id  = t2.customer_id 
                WHERE date(t1.create_time) <= date(t2.create_time) 
                AND t2.customer_id = '{customer_id}' AND t2.id = '{loan_app_id}'
                ) t 
            WHERE 
            t.rn = 1
        """
        return sql

    def td_sql(self, customer_id, loan_app_id):
        sql = f"""SELECT 
            t.customer_id,
            t.loan_app_id,
            t.result 
            FROM t_tongdun_body_guard t WHERE
            t.customer_id = '{customer_id}'
            AND
            t.loan_app_id = '{loan_app_id}'
            limit 1
        """
        return sql
