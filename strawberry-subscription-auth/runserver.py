import subprocess                                                               
                                                                                   
def uvicorn_run():                                                                   
    cmd =['uvicorn', 'strawberry_subscription_auth.main:app', '--reload']                                                                 
    subprocess.run(cmd) 


