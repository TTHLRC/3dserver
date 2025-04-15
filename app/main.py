from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
import psycopg2
from psycopg2 import Error
from psycopg2.extras import DictCursor

from app.database.database import get_db_connection
from app.api import auth
from app.schemas import schemas

app = FastAPI()

# 注册接口
@app.post("/register")
def register(user: schemas.UserCreate):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # 检查邮箱是否已存在
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # 创建新用户
        hashed_password = auth.get_password_hash(user.password)
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s) RETURNING id",
            (user.username, user.email, hashed_password)
        )
        connection.commit()
        
        return {"status": "success", "message": "User registered successfully"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection:
            cursor.close()
            connection.close()

# 登录接口
@app.post("/login", response_model=schemas.Token)
async def login_for_access_token(login_data: schemas.Login):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        
        # 根据用户名或邮箱查询用户
        if login_data.username:
            cursor.execute("SELECT * FROM users WHERE username = %s", (login_data.username,))
        else:
            cursor.execute("SELECT * FROM users WHERE email = %s", (login_data.email,))
            
        user = cursor.fetchone()
        
        if not user or not auth.verify_password(login_data.password, user['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user['username']}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection:
            cursor.close()
            connection.close()

# 保存数据接口
@app.post("/addData")
def create_user_data(
    data: schemas.ThreeDData,
    current_user: dict = Depends(auth.get_current_user)
):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        
        # 检查用户是否已有数据
        cursor.execute("SELECT id FROM user_data WHERE user_id = %s", (current_user['id'],))
        existing_data = cursor.fetchone()
        
        if existing_data:
            # 更新数据
            cursor.execute(
                "UPDATE user_data SET content = %s WHERE user_id = %s",
                (data.json(), current_user['id'])
            )
        else:
            # 创建新数据
            cursor.execute(
                "INSERT INTO user_data (content, user_id) VALUES (%s, %s)",
                (data.json(), current_user['id'])
            )
        
        connection.commit()
        return {"status": "success", "message": "Data saved successfully"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection:
            cursor.close()
            connection.close()

# 获取数据接口
@app.get("/getData", response_model=schemas.UserData)
def read_user_data(current_user: dict = Depends(auth.get_current_user)):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data WHERE user_id = %s", (current_user['id'],))
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="No data found for this user")
        
        return user_data
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection:
            cursor.close()
            connection.close() 