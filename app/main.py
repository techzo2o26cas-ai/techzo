from fastapi import FastAPI, HTTPException
from ai.predictor import predict_data
from db.database import users_collection as userTable , posts_collection as postTable , comments_collection as commentTable ,removed_collection as removeTbale
from core.add_Comment import CommentRequest
from core.users import NewUser
from fastapi.middleware.cors import CORSMiddleware
from core.security import hash_password,encode_response,decode_response,verify_password
from bson import ObjectId
from core.update_post import Update,Post

app = FastAPI(title="Cyberbullying Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#root endpont
@app.get("/")
def root():
    return {"message": "Cyberbullying API is running"}


#comment prediction and aproval endpoint
@app.post("/addcomment")
async def predict(data: CommentRequest):
    result = predict_data(data.comment)
    
    if result["bullying"]:
       
       remove_cmt_dict = CommentRequest.dict(data)
       remove_cmt_dict["post_id"] = decode_response(remove_cmt_dict["post_id"]) 
       remove_cmt_dict["user_id"] = decode_response(remove_cmt_dict["user_id"]) 
       remove_cmt_dict["confidence"] = round(float(result["confidence"]))

       await removeTbale.insert_one(remove_cmt_dict)
       return {
            "bullying": bool(result["bullying"]),
            "confidence": round(float(result["confidence"])),
            "message":"comment regected due to our cyberbulliying policy"
            }
    else:
        comment_dict = CommentRequest.dict(data)
        comment_dict["post_id"] = decode_response(comment_dict["post_id"]) 
        comment_dict["user_id"] = decode_response(comment_dict["user_id"]) 
        await commentTable.insert_one(comment_dict)
        return{
            "message":"comment added successfully"
        }
    

#add new user endpoint
@app.post("/user")   
async def create_user(user:NewUser):
    user_dict =NewUser.dict(user)
    user_dict["password"]= hash_password(user_dict["password"])
    user_dict["email"]=encode_response(user_dict["email"])
    user_dict["role"] = "user"
    response =await userTable.insert_one(user_dict)

    if response.inserted_id:
        return{"message":"user created successfully"}
    else:
        return {"message":"user creation failed"}
    

#user login endpoint
@app.post("/login")
async def login_user(email:str,password:str):
    h_password = hash_password(password)
    user = await userTable.find_one({"email": encode_response(email)})

    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    if not verify_password(password,user['password']):
        raise HTTPException(status_code=401, detail="invalid credentials")

    return{"message":"login successfully","user_id":encode_response(str(user["_id"])),"name":user["name"],"role":user["role"]}


#add post endpoint
@app.post("/addpost/{user_id}")
async def add_post(user_id,post:Post):
    post_dict = Post.dict(post)
    post_content = post_dict["post_content"]
    verify_post =  predict_data(post_content)
    if verify_post["bullying"]:
        return{
            "message":"post contains cyberbullying contecnt and cannot be added"
        }
    else:
        post_data = {
            "user_id":decode_response(user_id),
            "post_content":post_content
        }
        resposne = await postTable.insert_one(post_data)
        if resposne.inserted_id:
            return{"message":"post added successfully"}
        
        else:
            return{"message":"post addition failed"}


#fetch user endpoint
@app.get("/userdetails/{user_id}")
async def get_user_details(user_id):
     
     user_id_decoded = decode_response(user_id)

     if user_id_decoded is None:
       raise HTTPException(status_code=400, detail="invalid user id")

     user = await userTable.find_one({"_id": ObjectId(user_id_decoded)})
     
     if user:
         return{
                "name": user["name"],
                "email": decode_response(user["email"])
         } 
     else:
         raise HTTPException(status_code=404,detail="user not found")
     
   
#all users endpoint
@app.get("/users")
async def get_all_users():
    users =[]
    full_table = userTable.find()
    async for user in full_table:
        users.append({
            "user_id": encode_response(str(user["_id"])),
            "name":user["name"],
            "email":decode_response(user["email"])
        })
    return users

#all post endpoint
@app.get("/posts")
async def get_all_posts():
    posts =[]
    full_table = postTable.find()
    async for post in full_table:
        posts.append({
            "post_id":encode_response(str(post["_id"])),
            "user_id":encode_response(str(post["user_id"])),
            "post_comment":post["post_content"]
        })

    return posts

#fetch a post
@app.get("/getpost/{post_id}")
async def get_a_post(post_id: str):

    decoded_post_id = decode_response(post_id)

    if not decoded_post_id:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    # Validate ObjectId safely
    try:
        object_id = ObjectId(decoded_post_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    result = await postTable.find_one({"_id": object_id})

    if result is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post_id": encode_response(str(result["_id"])),
        "user_id": encode_response(result["user_id"]),
        "post": result["post_content"]
    }
    

 #update post   
@app.put("/updatepost/{id}")
async def update_post(id,post_content:Update):
    
    decoded_post_id = decode_response(id)
      
    if decoded_post_id is None:
          raise HTTPException(status_code=400 , detail="invalid id")
      
    else:
          post = await postTable.find_one({"_id":ObjectId(decoded_post_id)})

    if not post:
          raise HTTPException(status_code=404 , detail="post not found")
        
    newpost = post_content.dict(exclude_unset=True)
    if not newpost:
       raise HTTPException(status_code=400 , detail="no data proveded to update post")
    
   
    filterd_content = post_content.filter_content()
    if filterd_content is None:
        return({"message":"This post violate our policy so you can not update "})


    result = postTable.update_one(
         {"_id": ObjectId(decoded_post_id)},
        {"$set": newpost}
    )

    return{
        "message":"post updated successfully",
        "updated post":newpost
    }

#delete post
@app.delete("/delete/{post_id}")
async def delete_post(post_id):

    decoded_post_id = decode_response(post_id)

    if decoded_post_id is None:
        raise HTTPException(status_code=400 , detail="invalid post id")
    
    result = await postTable.delete_one({"_id": ObjectId(decoded_post_id)})

    if result.deleted_count==0:
        raise HTTPException(status_code=404, detail="post not found")
    return({"message":"deleted post successfully"})


# delete user
@app.delete("/deleteuser/{user_id}")
async def delete_user(user_id):
    decoded_user_id = decode_response(user_id)
    if decoded_user_id is None:
        raise HTTPException(status_code=400 , detail="invalid id")
    
    user_id = ObjectId(decoded_user_id) 

    result = await userTable.delete_one({"_id":user_id})
    if result.deleted_count==0:
        raise HTTPException(status_code=400 , detail="user not found")
    return({"message":"user deleted successfully"})



#get post
@app.get("/getcomment/{post_id}")
async def get_comment(post_id: str): 
    decoded_post_id = decode_response(post_id) 
    
    if decoded_post_id is None:
        raise HTTPException(status_code=400, detail="Invalid ID")
    
   
    cursor = commentTable.find({"post_id": decoded_post_id})

    data = []

    # Motor uses "async for" to iterate over the cursor
    async for comment in cursor:
        data.append({
            # Assuming user_id needs encoding for the frontend
            "id": encode_response(str(comment["user_id"])), 
            "comment": comment["comment"]
        })

    return {"data": data}

#remoed comments for admin
@app.get("/getrmvcomment")
async def get_rm_comment(): 
   
    cursor = removeTbale.find()

    data = []

    # Motor uses "async for" to iterate over the cursor
    async for comment in cursor:
        data.append({
            # Assuming user_id needs encoding for the frontend
            "id": encode_response(str(comment["_id"])), 
            "user_id":encode_response(comment["user_id"]),
            "comment": comment["comment"]
        })

    return {"data": data}

#user post
@app.get("/getallpost/{user_id}")
async def getpost(user_id):
    decoded_id = decode_response(user_id)
    if decoded_id is None:
      raise HTTPException(status_code=400 , detail="invalid id")
    
    cursor = postTable.find({"user_id":decoded_id})

    data=[]
    
    
    async for post in cursor:
        data.append({
            
            "id": encode_response(str(post["_id"])), 
            "post": post["post_content"]
        })

    return {"data": data}

#total user
@app.get("/admin")
async def admin():
    users = await userTable.count_documents({})
    total_users = users

    total_posts = await postTable.count_documents({})

    total_comments = await commentTable.count_documents({})

    total_bad_comments = await removeTbale.count_documents({})

    return({
        "total_user":total_users,
        "total_posts":total_posts,
        "total_comments":total_comments,
        "total_ bad_comments":total_bad_comments
    })

#delete remove comment
@app.delete("/deleteremovecmt/{c_id}")
async def delete_cmt(c_id):
    c_id = decode_response(c_id)
    if c_id is None:
        raise HTTPException(status_code=400 , detail="invalid id")
    
    _id = ObjectId(c_id) 
   
    result = await removeTbale.delete_one({"_id":_id})
    if result.deleted_count==0:
        raise HTTPException(status_code=400 , detail="user not found")
    
    return({"message":"user deleted successfully"})
 