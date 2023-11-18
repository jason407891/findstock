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

function search(){
    let currentPath = window.location.pathname;
    fetch("/api/"+currentPath)
    .then(response=>response.json())
    .then(data=>{
        let productList= data.data;
        let showProduct = document.querySelector(".ptdata");
        productList.forEach(product=>{
            let productelement =document.createElement("div");
            console.log(product);
            productelement.innerHTML=`
            <span>製造商:${product.mfr}<span><span>產品編號:${product.pn}<span><span>庫存數量:${product.qty}<span><br>
            `;
            showProduct.appendChild(productelement);
        });
        })
    .catch(error=>{
        console.log("something error",error)
    });
}