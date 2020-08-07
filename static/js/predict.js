window.onload = function(){
  let pred = document.getElementById("prediction");
  let st = document.getElementById("start");
  let sp = document.getElementById("stop");
  let im = document.getElementById("image");
  let vd = document.getElementById("videostyle");
  let ims = document.getElementById("imagestyle");


  var canvas1 = document.querySelector('.visualizer');
  // console.log(canvas1);
  var canvasCtx = canvas1.getContext("2d");

  //let video = document.querySelector('#videoElement');
//Global variable
  var base64data
  var label
  var prob
  //Take permission to record audio and then send stream
  navigator.mediaDevices.getUserMedia({audio:true,video:true })
        .then(stream => {handlerFunction(stream)});

  let video = document.querySelector("#videoElement");
  let canvas = document.querySelector("#canvasElement");
  var canvasCtx
  let ctx = canvas.getContext('2d');


  socket.on("label_event",function(message){
    console.log(message)
    label = message["label"]
    prob = parseFloat(message["prob"])
     if (label === "wet cough" || label == "dry cough"){
        if (label == "dry cough" && prob >= 0.50){
         pred.innerHTML = "Dry Cough"
         }
         else{
           pred.innerHTML = "Wet Cough"
         }
       }
     else{
         if (stopRecord.disabled == true){
             pred.innerHTML = ""
           }
         else
           {
           pred.innerHTML = "Not Cough";

           }

        }

    });


  var localMediaStream = null;
  function sendSnapshot() {

      if (!localMediaStream) {
        return;
        }

      ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight, 0, 0, 300, 150);
      // console.log("Inside sendSnapshot")
      let dataURL = canvas.toDataURL('image/jpeg');
      socket.emit('input_image', dataURL);

    }


  //Function to handle the input stream
      function handlerFunction(stream) {
        //Stores the stream

        window.rec = new MediaRecorder(stream);

        visualize(stream);
        localMediaStream = stream;
        video.style.display = "none";

        rec.onstart = e =>{

          totalaudio = [];

          }

        //Task when audio is inputted into the stream
        rec.ondataavailable = e => {

          //Add data to the audio buffer
          totalaudio.push(e.data);

        }

        //Task when audio is stopped
        rec.onstop = e =>{
          //Print length of buffer
          console.log(totalaudio.length)
          //Create blob of the new audio
          let blob = new Blob(totalaudio);
          //Send blob to the backend
          if(isConnected == true){
            console.log(isConnected)
            sendData(blob)
          }
        }

        //Interval function to interrupt the recording every 5 seconds.
        setInterval(function(){
          //If the recording has started, interrupt.
          if(rec.state == "recording"){

            rec.stop()
            totalaudio = []
            rec.start()

            }
          //6000 as it is always a second less = 5000ms
        }, 6000);

        setInterval(function () {
            if(rec.state == "recording"){
              // console.log("Sending snapshot")
              sendSnapshot();
            }
          }, 1000);

        }




        //Send blob for audio processing
      async function sendData(data) {

           console.log(data)
           //Upload the blob to a file reader
           var reader = new FileReader();
           reader.readAsDataURL(data);
           //Converting it to a base64 string.
           reader.onload = function() {
             // console.log("reader onload ");
                base64data = reader.result.split(',')[1];
                //console.log(base64data);
                socket.emit("blob_event",base64data)
           }



          /*
          var element = document.getElementById("container1");


          // Add an event listener
          pred.addEventListener("Trigger", function(e) {
            console.log(e.detail.message); // Prints "Example of an event"
            pred.innerHTML =" ";
            element.style.display ="block";

          });

          // Create the event
          var event = new CustomEvent("Trigger", { "detail": {
            message : "You Coughed!",
            } });

          if ((label === "coughing")&&(prob>=0.75)){
              pred.dispatchEvent(event);
              }
          else{
              if (stopRecord.disabled == true){
                  pred.innerHTML = ""
                }
              else
                {
                pred.innerHTML = "Detecting...";
                }
                element.style.display = "none";
              } */


          }



           // When start button is clicked.

          record.onclick = e => {

            st.innerHTML = "Started recording"
            st.style.backgroundColor = "white"
            sp.innerHTML = ""
            pred.innerHTML = "Detecting..."
            video.style.display = "inline-block"
            video.srcObject = localMediaStream
            im.style.display = "inline-block"
            vd.style.display = "inline-block"
            ims.style.display = "flex"
            canvas1.style.display = "inline-block"

            console.log('Start:I was clicked')
            record.disabled = true;
            record.style.backgroundColor = " is no sleep function like that in JavaSgrey"
            stopRecord.disabled=false;
            if(isConnected == true){
            socket.emit('started', "Started Feed");
            rec.start();
            }
            else {
             console.log("Server not connected")
            }


          }

          //When stop button is clicked.
          stopRecord.onclick = e => {

            st.innerHTML = ""
            sp.innerHTML = "Stopped recording"
            sp.style.backgroundColor = "#f4623a"
            pred.innerHTML = ""
            video.srcObject = null;
            video.style.display = "none"
            im.style.display = "none"
            vd.style.display = "none"
            ims.style.display = "none"
            canvas1.style.display = "none"

            console.log("Stop:I was clicked")
            record.disabled = false;
            stopRecord.disabled=true;
            record.style.backgroundColor = "white"

            socket.emit('stopped', "Stopped Feed");
            rec.stop();

          }

          function visualize(stream) {
              audioCtx = new AudioContext();


              const source = audioCtx.createMediaStreamSource(stream);

              const analyser = audioCtx.createAnalyser();
              analyser.fftSize = 2048;
              const bufferLength = analyser.frequencyBinCount;
              const dataArray = new Uint8Array(bufferLength);

              source.connect(analyser);
              //analyser.connect(audioCtx.destination);

              draw()

              function draw() {
                const WIDTH = canvas1.width
                const HEIGHT = canvas1.height;

                requestAnimationFrame(draw);

                analyser.getByteTimeDomainData(dataArray);

                canvasCtx.fillStyle = 'rgb(200, 200, 200)';
                canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

                canvasCtx.lineWidth = 2;
                canvasCtx.strokeStyle = 'rgb(0, 0, 0)';

                canvasCtx.beginPath();

                let sliceWidth = WIDTH * 1.0 / bufferLength;
                let x = 0;


                for(let i = 0; i < bufferLength; i++) {

                  let v = dataArray[i] / 128.0;
                  let y = v * HEIGHT/2;

                  if(i === 0) {
                    canvasCtx.moveTo(x, y);
                  } else {
                    canvasCtx.lineTo(x, y);
                  }

                  x += sliceWidth;
                }

                canvasCtx.lineTo(canvas1.width, canvas1.height/2);
                canvasCtx.stroke();

              }
            }
      }
