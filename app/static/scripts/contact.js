

function Send() {
    var first_name = document.getElementById("first-name").value;
    var last_name = document.getElementById("last-name").value;
    var email = document.getElementById("mailid").value; 
    var number = document.getElementById("number").value;
    var message = document.getElementById("message").value;

    var name = first_name + " " + last_name;

    var body = "Name: " + name + "<br/> Email: " + email + "<br/> Mobile No: " + number + "<br/> Message: " + message;
    console.log(body);

    Email.send({
        SecureToken: "90af19be-3f96-4819-b5e0-b9d1152480e9",
        To: "inquiries1424@gmail.com",
        From: "inquiries1424@gmail.com",
        Subject: name,
        Body: body
    }).then(
        message => {
        if (message == 'OK') {
          swal("Successful!", "Your Message Successfully Received!", "success");
          // Clear input fields
          document.getElementById("first-name").value = "";
          document.getElementById("last-name").value = "";
          document.getElementById("mailid").value = ""; 
          document.getElementById("number").value = "";
          document.getElementById("message").value = "";
        } else {
          swal("Something Wrong", "Your Message is not Received!", "error");
        }
      }
    );
  }
