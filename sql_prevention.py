from passlib.hash import pbkdf2_sha256 

if pbkdf2_sha256.identify("my_password"): 
	print("The password is strong.") 
else: 
	print("The password is weak.") 