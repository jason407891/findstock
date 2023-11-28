function goindex(){
    window.location.href="/";
}

function gostock(){
    window.location.href="/stock";

}
function gobom(){
    window.location.href="/bom";

}
function gocontact(){
    window.location.href="/contact";

}

function golist(){
    let pn=document.querySelector(".search-bar").value;
    window.location.href="/product/"+pn;
}
function gorfq(){
    window.location.href="/rfq";

}

function search(){
    return new Promise((resolve, reject)=>{
    let currentPath = window.location.pathname;
    fetch("/api/"+currentPath)
    .then(response=>response.json())
    .then(data=>{
        let productList= data.data;
        let showProduct = document.querySelector(".tbody");
        showProduct.innerHTML="";
        productList.forEach(product=>{
            let row =document.createElement("tr");
            row.id=row_id;
            //處理價格
            let priceContent="";
            product.price.forEach(priceItem=>{
                priceContent+=`
                <div>數量: <span class="break_qty">${priceItem.goods_num}</span>, 價格: <span class="break_price">${priceItem.goods_price}</span></div>
                `;
            })
            row.innerHTML = `
                <td id=${row_id}>${product.date}</td>
                <td class="searchresult_pn" id=${row_id}>${product.pn}</td>
                <td class="searchresult_mfr" id=${row_id}>${product.mfr}</td>
                <td class="searchresult_remark" id=${row_id}>
                    <div>倉庫地點: ${product.location}</div>
                    <div>製造日期: ${product.dc}</div>
                    <div>產地: ${product.coo}</div>
                    <div>其他資訊: ${product.noted}</div>
                </td>
                <td id=${row_id}>${product.qty}</td>
                <td id=${row_id}>
                    <div class="pricebreak_data">${priceContent}</div>
                </td>
                <td id=${row_id}>
                    <span>數量</span><input id=${row_id} class="demand_qty" type="number">
                    <button onclick=addItemtoRFQ(this) id=${row_id}>加入詢價單</button>
                </td>
            `;

            showProduct.appendChild(row);
            row_id+=1;
        });
        resolve();
        })
    .catch(error=>{
        console.log("something error",error);
        reject(error);
    });})
}

function agentLoad(){
    let currentPath = window.location.pathname;
    fetch("/api/agent"+currentPath)
    .then(response=>response.json())
    .then(data=>{
      let agentList= data.data;
      let showProduct = document.querySelector(".agenttbody");
      showProduct.innerHTML="";
      agentList.forEach(productList=>{
        productList.forEach(product=>{
            let row =document.createElement("tr");
            row.id=row_id;
            //處理價格
            let priceContent="";
            product.price.forEach(priceItem=>{
                priceContent+=`
                <div>數量: <span class="break_qty">${priceItem.goods_num}</span>, 價格: <span class="break_price">${priceItem.goods_price}</span></div>
                `;
            })
            row.innerHTML = `
                <td id=${row_id}>${product.date}</td>
                <td class="searchresult_pn" id=${row_id}>${product.pn}</td>
                <td class="searchresult_mfr" id=${row_id}>${product.mfr}</td>
                <td class="searchresult_remark" id=${row_id}>
                    <div>代理商庫存供參考</div>
                </td>
                <td id=${row_id}>${product.stock}</td>
                <td id=${row_id}>
                    <div class="pricebreak_data">${priceContent}</div>
                </td>
                <td id=${row_id}>
                    <span>數量</span><input id=${row_id} class="demand_qty" type="number">
                    <button onclick=addItemtoRFQ(this) id=${row_id}>加入詢價單</button>
                </td>
            `;
            showProduct.appendChild(row);
            row_id+=1;
      });
    })
    })

  }

function showList(){
    return new Promise((resolve, reject) => {

    let titlearea =document.querySelector(".bodylist");
    titlearea.innerHTML=``;
    let uppercontent =document.createElement("div");
    uppercontent.innerHTML=`
        <div class="account" id="logstatus">
            <span class="account-content" onclick="sign_in()">登入</span>
            <span class="account-content" onclick="register()">註冊</span>
        </div>
        <hr>
        <a href="/" class="index_title">FINDSTOCK電子元件商城</a>
        </br>
        <div class="search_area">
            <div class="search">
                <input placeholder="請輸入產品編號" class="search-bar" onkeypress="handle_search(event)"></input>
                <div class="search_btn" onclick="golist()">
                    <img src="../static/search.png" class="search-icon" onmouseover="style.opacity=0.7" onmouseout="style.opacity=1"></img>
                </div>
                <span class="search_many"onclick="searchmany_open()" onmouseover="style.opacity=0.7" onmouseout="style.opacity=1">批量搜尋</span>
            </div>
        </div>
        </br>    
        </br>
        <hr>
        <div class="select">
            <span class="select-btn" onmouseover="style.opacity=0.7" onmouseout="style.opacity=1" onclick="goindex()">首頁</span>
            <span class="select-btn" onmouseover="style.opacity=0.7" onmouseout="style.opacity=1" onclick="gostock()">庫存上傳</span>
            <span class="select-btn" onmouseover="style.opacity=0.7" onmouseout="style.opacity=1" onclick="gobom()">BOM表</span>
            <span class="select-btn" onmouseover="style.opacity=0.7" onmouseout="style.opacity=1" onclick="gorfq()">詢價單</span>
            <span class="select-btn" onmouseover="style.opacity=0.7" onmouseout="style.opacity=1" onclick="gocontact()">聯繫我們</span>
        </div>
        <!--註冊帳號的表單-->
        <div class="signup_block">
            <form class="signup">
                <div class="deco_bar"></div>
                <div class="signup_text">註冊會員帳號</div>
                <img src="../static/close.png" class="close_button" onclick="close_form()"></img>
                <input class="register_input" name="name" placeholder="*輸入聯絡人姓名*"></input>
                <input class="register_input" name="email" placeholder="*輸入電子郵件*"></input>
                <input class="register_input" name="password" placeholder="*輸入密碼*" type="password"></input>
                <input class="register_input" name="company_name" placeholder="*輸入公司名稱*"></input>
                <input class="register_input" name="phone" placeholder="輸入電話&分機"></input>
                <input class="register_input" name="tax_id" placeholder="輸入統編"></input>
                <input class="register_input" name="address" placeholder="輸入收件地址"></input>
                <input class="register_input" name="brand" placeholder="常用電子零件品牌/優勢品牌"></input>
                <div>備註: 註冊後可於庫存頁面上傳庫存</div>
    
                <input class="submit_btn" onclick="register_user()" value="註冊新帳戶"></input>
                <div class="signup_link"><span id="have_account">已經有帳戶了？</span><span onclick="sign_in()">點此登入</span></div>
            </form>
        </div>
    
        <!--登入會員的表單-->
        <div class="login_block">
            <div class="login">
                <div class="deco_bar"></div>
                <div class="login_text">登入會員帳號</div>
                <img src="../static/close.png" class="close_button" onclick="close_form()"></img>
                <input class="login_input" placeholder="輸入電子信箱"></input>
                <input class="login_input" placeholder="輸入密碼" type="password"></input>
                <input class="submit_btn" onclick="login()" value="登入帳戶"></input>
                <div class="login_link">還沒有帳戶？<span onclick="register()">點此註冊</span></div>
            </div>
        </div>
        <!--批量搜尋功能-->
        <div class="search_many_block">
            <div class="searchmany_form">
                <div class="mutiple_title">批量搜尋</div>
                <img src="../static/close.png" class="searchmany_close" onclick="searchmany_close()"></img>
                <div class="inputmuti_area">
                    <textarea class="mutiple_input" placeholder="將產品型號和數量複製到此處，支援多行"></textarea>
                </div>
                <div>範例:<br>
                    55100-0670 100<br>
                    PAP-02V-S 200
                </div><br>
                <div class="do_mutiplesearch" onclick="do_mutiplesearch()" onmouseover="style.opacity=0.7" onmouseout="style.opacity=1">開始搜尋</div>
            </div>
        </div>
    `;
    titlearea.append(uppercontent);
    resolve(); // 完成後，調用 resolve
    });
}


function do_mutiplesearch(){
    alert("批量搜尋，功能開發中");
}

function checkLogin(){
    let token = localStorage.getItem("token");
    if (token=="null"){
        alert("請先登入");
        window.location.href="/";
        return;
    }
}
function checkLogin_list(){
    let token = localStorage.getItem("token");
    if (token=="null"){
        alert("請先登入");
        window.location.reload()
        return;
    }
}

window.onload = function() {
    showList()
      .then(checkstatus)   
      .catch(error => console.error("An error occurred: ", error));
  };