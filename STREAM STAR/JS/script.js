function change(){
    var choice = document.getElementById('option').value

    if(choice=='tamil'){
        window.location.href="/HTML/MOVIES/index.html"
    }
    else if(choice=='telugu'){
        window.location.href="/HTML/MOVIES/telugu/index.html"
    }
    else{
        window.location.href="/HTML/MOVIES/malayalam/index.html"
    }
}

//login validations
function loginValidation(){
    var db=[{'USERNAME':'ravi','PASSWORD':'1234'},{'USERNAME':'vijay','PASSWORD':'1234'},{'USERNAME':'admin','PASSWORD':'1234'}]

    var Username = document.getElementById('username').value
    var Password = document.getElementById('password').value
    var flag=false

    for(var i=0;i<db.length;i++){
        if(db[i]['USERNAME']==Username){
            if(db[i]['PASSWORD']==Password){
                flag=true
            }
        }
    }
    if(flag==true){
        window.location.href='/HTML/home.html'
    }
    else{
        document.getElementById('error').innerHTML='Invalid Username Or Password'
    }
}
 //signup validations
 function signup(){
    var first_name = document.getElementById('first-name').value
    var last_name = document.getElementById('last-name').value

    //phone no validation
    var phone= document.getElementById('phone').value
    var phone_flag =false
    if((phone>=6000000000)&&(phone<=9999999999)){
        phone_flag=true
    }
    else{
        document.getElementById('error1').innerHTML="invalid Phone Number"
    }

    //email validation
    var email = document.getElementById('email').value
    var email_flag=false
    var email_flag1= false
    var email_flag2 = true
    for(var i=0;i<email.length;i++){
        if(email[i]=='@'){
            email_flag1=true
        }
        else if((email[i]>'A')&&(email[i]<='Z')){
            email_flag2=false
        }
    }
    if((email_flag1==true)&&(email_flag2==true)){
        email_flag=true
    }
    else{
        document.getElementById('error2').innerHTML="invalid email id"
    }

    //password validation
    var password = document.getElementById('new-pass').value
    var Password_flag= false
    var upper = 0
    var lower = 0
    var num = 0
    var special = 0
    for(var i=0;i<password.length;i++){
        if((password[i]>='A')&&(password[i]<='Z')){
            upper++
        }
        else if((password[i]>='a')&&(password[i]<='z')){
            lower++
        }
        else if((password[i]>=0)&&(password[i]<=9)){
            num++
        }
        else{
            special++
        }
    }
    if((password.length>=8)&&(password.length<=16)&&(upper>=1)&&(lower>=1)&&(num>=1)&&(special>=1)){
        Password_flag=true
    }
    else{
        document.getElementById('error3').innerHTML='invalid password'
    }

    //confrim password validation
    var con_password = document.getElementById('con-pass').value
    var con_password_flag=false

    if(con_password==password){
        con_password_flag=true
    }
    else{
        document.getElementById('error4').innerHTML="check conform password"
    }


    //all data valid
    if((phone_flag==true)&&(email_flag==true)&&(Password_flag==true)&&(con_password_flag==true)){
        window.location.href='/HTML/credentials/otp.html'
    }
}

//validation for forgot password
function send(){
    var input = document.getElementById('value').value
    var Not_a_no = true
    var phone_flag =false
    var email_flag=false
    var email_flag1= false
    var email_flag2 = true

    //check give given value is phone no or email
    for(var i=0;i<input.length;i++){
        if((input[i]>=0)&&(input[i]<=9)){
            Not_a_no=false            
        }
    }
    console.log(Not_a_no)

    if(Not_a_no==false){
        //phone no validation

        if((input>=6000000000)&&(input<=9999999999)){
            phone_flag=true
        }   
        else{
            document.getElementById('error').innerHTML="invalid Phone Number"
        }
    } 
    else{
        //email validation
        for(var i=0;i<input.length;i++){
            if(input[i]=='@'){
                email_flag1=true
            }
            else if((input[i]>'A')&&(input[i]<='Z')){
                email_flag2=false
            }
        }
        if((email_flag1==true)&&(email_flag2==true)){
            email_flag=true
        }
        else{
            document.getElementById('error').innerHTML="invalid email id"
        }
    }    

    if(phone_flag==true){
        window.location.href='/HTML/credentials/forgot_OTP.html'
    }
    else if(email_flag==true){
        window.location.href='/HTML/credentials/forgot_OTP.html'
    }

   }

function create(){
    //password validation
 var password = document.getElementById('new-pass').value
var Password_flag= false
var upper = 0
var lower = 0
var num = 0
var special = 0
for(var i=0;i<password.length;i++){
    if((password[i]>='A')&&(password[i]<='Z')){
        upper++
    }
    else if((password[i]>='a')&&(password[i]<='z')){
        lower++
    }
    else if((password[i]>=0)&&(password[i]<=9)){
        num++
    }
    else{
        special++
    }
}
if((upper>=1)&&(lower>=1)&&(num>=1)&&(special>=1)){
    if((password.length>=8)&&(password.length<=16)){
        Password_flag=true
    }
    else{
        document.getElementById('error').innerHTML="Password Length Should be '8 to 16' character "
    }
    
}
else{
    document.getElementById('error').innerHTML="Password Should Contain 'A-Z' 'a-z' '0-9' '@,$'"
}

//confrim password validation
var con_password = document.getElementById('con-pass').value
var con_password_flag=false

if(con_password==password){
    con_password_flag=true
}
else{
    document.getElementById('error').innerHTML="check conform password"
}

if((Password_flag==true)&&(con_password_flag==true)){
    window.location.href='/index.html'
}
} 