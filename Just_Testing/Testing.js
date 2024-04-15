const fs = require('fs');
const fetch = require('node-fetch'); // 'node-fetch' 모듈 불러오기

const clientId = '';
const clientSecret = '';

// language => 언어 코드 ( Kor, Jpn, Eng, Chn )
function stt(language, filePath) {
    const url = `https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=${language}`;
    const headers = {
        'Content-Type': 'application/octet-stream',
        'X-NCP-APIGW-API-KEY-ID': clientId,
        'X-NCP-APIGW-API-KEY': clientSecret
    };

    // 파일을 Buffer로 읽어오기
    const fileBuffer = fs.readFileSync(filePath);

    // fetch를 사용해 요청 보내기
    fetch(url, {
        method: 'POST',
        headers: headers,
        body: fileBuffer // Buffer를 body로 설정
    })
        .then(response => {
            console.log(response.status); // 응답 상태 코드 출력
            return response.text(); // 응답 본문을 텍스트로 변환
        })
        .then(body => {
            console.log(body); // 응답 본문 출력
        })
        .catch(err => {
            console.error(err); // 오류 출력
        });
}

stt('Kor', '../Hello.wav');
