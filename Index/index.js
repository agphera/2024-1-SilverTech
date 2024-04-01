//nav_bar burger mobile menu
function burgerOn() {
    var element = document.getElementById("nav-links");
    var name1 = document.getElementById("nav_title1");
    var name2 = document.getElementById("nav_title2");
    var name3 = document.getElementById("nav_title3");
    var name4 = document.getElementById("nav_title4");
    
    if (element.className === "navbar-menu is-centered") {
      element.className = "is-active navbar-menu is-centered";
      name1.className = "nav_hover text_colorBlack";
      name2.className = "nav_hover text_colorBlack";
      name3.className = "nav_hover text_colorBlack";
      name4.className = "nav_hover text_colorBlack";
    } else {
      element.className = "navbar-menu is-centered";
      name1.className = "nav_hover text_color";
      name2.className = "nav_hover text_color";
      name3.className = "nav_hover text_color";
      name4.className = "nav_hover text_color";
    }

}


//모든 학습파일
function visible(current, total){
  var arr = [];
  for(let k = 0; k< total; k++){
    arr[k] = k+"text";
  }
  var con = document.getElementById(arr[current]);
  for(let j = 0; j<arr.length; j++){
    var hid = document.getElementById(arr[j]);
    hid.style.display = 'none';
  }	
  con.style.display = 'block'; 	
  
}










