
//랜덤 인사 출력
document.addEventListener('DOMContentLoaded', function() {
    var greetings = ["반갑습니다!", "안녕하세요!", "환영합니다!", "어서오세요!"];
    var randomGreeting = greetings[Math.floor(Math.random() * greetings.length)]; // Choose a random greeting
    document.getElementById('greeting').textContent = randomGreeting; // Display it in the 'greeting' element
});
