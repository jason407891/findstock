function register_user(){
    let nameInput = document.querySelector('.register_input[name="name"]');
    let emailInput = document.querySelector('.register_input[name="email"]');
    let passwordInput = document.querySelector('.register_input[name="password"]');
    let phoneInput = document.querySelector('.register_input[name="phone"]');
    let company_nameInput = document.querySelector('.register_input[name="company_name"]');
    let tax_idInput = document.querySelector('.register_input[name="tax_id"]');
    let addressInput = document.querySelector('.register_input[name="address"]');
    let brandInput = document.querySelector('.register_input[name="brand"]');

    
    if (!nameInput.value || !emailInput.value || !passwordInput.value || !company_nameInput.value) {
        console.log("請填寫所有欄位");
        let displayarea=document.querySelector(".signup_link");
        displayarea.innerHTML="請填寫所有必填欄位";
        return;
        }   
    let userdata={
        name: nameInput.value,
        email: emailInput.value,
        password: passwordInput.value,
        phone: phoneInput.value,
        company_name: company_nameInput.value,
        tax_id: tax_idInput.value,
        address: addressInput.value,
        brand: brandInput.value
    };
    fetch("/api/user",{
        method:"POST",
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(userdata),
    })
    .then(response=>{
        if(!response.ok){
            if(response.status===400){
                let displayarea=document.querySelector(".signup_link");
                displayarea.innerHTML="EMAIL已經被註冊過!";
                displayarea.id="have_account";
            }
        }
        return response.json();
    })
    .then(data=>{
        if (data.ok) {
            console.log('User created successfully');
            alert("註冊成功");
        } else {
            console.error('User creation failed:', data.message);
        }
    })
    .catch(error=>{
        console.error("fetch problem",error)
    });
}

function sign_in(){
    let register = document.querySelector('.signup_block');
    let signin = document.querySelector('.login_block');
    signin.style.display="flex";
    register.style.display="none";
}

function register(){
    let register = document.querySelector('.signup_block');
    let signin = document.querySelector('.login_block');
    signin.style.display="none";
    register.style.display="flex";
}

function close_form(){
    let register = document.querySelector('.signup_block');
    let signin = document.querySelector('.login_block');
    signin.style.display="none";
    register.style.display="none";
}
function searchmany_open(){
    let serach_many = document.querySelector('.searchmany_form');
    serach_many.style.display="flex";
}
function searchmany_close(){
    let serach_many = document.querySelector('.searchmany_form');
    serach_many.style.display="none";
}

function handle_search(event){
    if (event.keyCode===13){
        golist();
    }
}

function login(){
    let email = document.getElementsByClassName("login_input")[0].value;
    let password = document.getElementsByClassName("login_input")[1].value;

    fetch("/api/user/auth", {
        method: "PUT",
        headers: {
                "Content-Type": "application/json"
            },
        body: JSON.stringify({ email, password })
        })
    .then(response => {
        if (!response.ok) {
            if(response.status===400){
                let displayarea=document.querySelector(".login_link");
                displayarea.innerHTML="帳號或是密碼錯誤!";
                return;
            }
        }
        return response.json();
        })
    .then(data => {
        if(data==undefined){console.log("帳號或是密碼錯誤");}
        else{
        localStorage.setItem("token", data.token);
        localStorage.setItem("company_name", data.company_name);
        close_form();
        let display_memeber=document.querySelector("#logstatus");
        console.log(display_memeber);
        display_memeber.innerHTML="登出系統";
        display_memeber.id="logout";
        display_memeber.onclick=logout;
        let cur_url=window.location.href;
        window.location.href=cur_url;
    }
        
        })
    .catch(error => {
            console.error("Login error:", error);
        })
}

function checkstatus(){
    let token = localStorage.getItem("token");
    let headers = new Headers({
        "Authorization": token,
        "Content-Type": "application/json"
    });
    fetch("/api/user/auth", {
        method: "GET",
        headers: headers
    })
    .then(response=>response.json())
    .then(data=>{
        if (data.error){
            //未登入時的標籤id是logstatus
            let display_status=document.querySelector("#logstatus");
            console.log("用戶未登入")
            display_status.innerHTML="登入/註冊";
            display_status.id="logstatus";
            display_status.onclick=sign_in;
        }
        else{
            //已登入時的標籤id是logout
            let display_status=document.querySelector("#logout");
            if(display_status){
                display_status.innerHTML="登出系統";
                display_status.id="logout";
                display_status.onclick=logout;}
            else{
                display_status=document.querySelector("#logstatus");
                display_status.innerHTML="登出系統";
                display_status.id="logout";
                display_status.onclick=logout;}
            }
        }
    )
    .catch(()=>{
        console.log("發生錯誤");
    })
}


function logout(){
    let logout_member = document.querySelector("#logout");
    logout_member.innerHTML="登入/註冊";
    logout_member.id="logstatus";
    logout_member.onclick=sign_in;
    localStorage.setItem("token", null);
    localStorage.setItem("company_name", null);
    setTimeout(function(){window.location.reload()},100)
}


function schedule_page(){
    let token = localStorage.getItem("token");
    console.log(token);
    if (token == "null"){
        sign_in();
    }
    else{
        window.location.href="/booking";
    }
}


function getsupplier(){
    let company_name = localStorage.getItem("company_name");
    return company_name
}



window.onload=function(){
    checkstatus();
    setTimeout(function(){
        console.log("already check user status");
    }, 500);
}