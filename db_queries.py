sql = {
    "get_all_users": "select name from users",

    "authenticate_user": """
        select 
            name as account,
            CASE 
                 WHEN count() == 0 THEN false
                 WHEN count() == 1 THEN true
                 ELSE false  
            END AS authenticated
        from users 
        where name = '${name}' 
        and password_hash = '${password_hash}'
    """,

    "register_user": """
        INSERT INTO users (name, password_hash)
        VALUES('${name}', '${password_hash}');
    """,
}