import { showPopup, hidePopup} from './popup.js';

document.addEventListener("DOMContentLoaded", function() {
    let container = document.querySelector('.navbar-progress-container');
    let progressBar = document.querySelector('progress');
    let analysis_popup = document.getElementById("analysisPopup");
    let exitPopup=document.getElementById("exitPopup");
    //let messageContainer = document.getElementById("messageContainer"); // 비슷한것같나요 메시지 컨테이너
    //let imagePopup = document.getElementById("imagePopup"); // 비교이미지 팝업
  
    /*시간 설정*/
    let duration = 15000; // 프로그레스바 15초
    //let hideDuration = 30000; // navbar+progressbar 사라지는 시간 30초(변수만 설정, 아직 미구현)
  
    /*프로그레스바 감소*/
    function updateProgressBar() {
      let decrementAmount = progressBar.max / (duration / 100); // Calculate decrement per 100ms
      progressBar.value -= decrementAmount;
      if (progressBar.value <= 0) {
        clearInterval(progressInterval);
        hideElements(); //프로그레스바 0 -> 요소사라짐
      }
    }  


    showPopup("letStartPopup");
    setTimeout(() => {
      hidePopup("letStartPopup"); //5초뒤 사라짐                   
    }, 5000);

    let progressInterval = setInterval(updateProgressBar, 100);  

  
    /*navbar+progressbar 사라짐 + 로딩중 팝업 */
    function hideElements(){

      analysis_popup.style.display = "flex"; //analysis popup 보이기 
      showPopup("analysisPopup");
      

      //hidePopup("analysisPopup");

      
      showElements(); //navbar+progressbar 다시 보여주는 함수

    }
  
    function showElements() { //여기에 비교 텍스트, 비교이미지 보여주는 것 구현 추가할 예정
      container.style.transform = 'translateY(0)'; //navbar+progress bar 다시 보여주기
      container.style.opacity = 1;
    }

  });
  

  //도움말 버튼 전체 동작 관리
  document.getElementById("helpButton").addEventListener("click", function() {
    showPopup("helpPopup");
  });

  document.getElementById("one").addEventListener("click", function() {
    showPopup("onePopup");
  });

  document.getElementById("two").addEventListener("click", function() {
      showPopup("twoPopup");
  });

  document.getElementById("three").addEventListener("click", function() {
      showPopup("threePopup");
  });

  document.getElementById("four").addEventListener("click", function() {
      showPopup("fourPopup");
  });

  document.getElementById("back").addEventListener("click", function() {
      hidePopup("helpPopup");
  });

  document.getElementById("bbackOne").addEventListener("click", function() {
      hidePopup("onePopup");
  });

  document.getElementById("bbackTwo").addEventListener("click", function() {
      hidePopup("twoPopup");
  });

  document.getElementById("bbackThree").addEventListener("click", function() {
      hidePopup("threePopup");
  });

  document.getElementById("bbackFour").addEventListener("click", function() {
      hidePopup("fourPopup");
  });
//도움말 버튼 완료

  
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
  
  
  
  console.log("보내기");console.log("보내기");console.log("보내기");console.log("보내기");
  
  
