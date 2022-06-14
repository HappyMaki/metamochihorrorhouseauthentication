sql = {
    "get_all_users": "select name from users",

    "authenticate_user": """
        select 
            name as name,
            CASE 
                 WHEN count() == 0 THEN false
                 WHEN count() == 1 THEN true
                 ELSE false  
            END AS success
        from users 
        where name = '${name}' 
        and password_hash = '${password_hash}'
    """,

    "register_user": """
        INSERT INTO users (name, password_hash)
        VALUES('${name}', '${password_hash}');
    """,

    "get_character_data": """
        SELECT
            character_creation_data
        FROM users
        where name = '${name}' 
    """,

    "set_character_data": """
        UPDATE users
        SET character_creation_data = '${character_data}'
        WHERE name = "${name}"
    """
}