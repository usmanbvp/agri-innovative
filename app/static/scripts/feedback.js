  
document.addEventListener('DOMContentLoaded', () => {
  const openFormButton = document.getElementById('openForm');
  const closeFormButton = document.getElementById('closeForm');
  const feedbackForm = document.getElementById('feedbackForm');

  openFormButton.addEventListener('click', () => {
    feedbackForm.style.display = 'block';
  });

  closeFormButton.addEventListener('click', () => {
    feedbackForm.style.display = 'none';
  });

  document.getElementById('submitFeedback').addEventListener('click', () => {
    // Call the Send() function when the button is clicked
    Send();
  });
});

function Send() {
  var name = document.getElementById("name").value;
  var email = document.getElementById("email").value;
  var feedback = document.getElementById("feedback").value;

  var body = "Name: " + name + "<br/>Email: " + email + "<br/>Feedback: " + feedback;

  Email.send({
    SecureToken: "90af19be-3f96-4819-b5e0-b9d1152480e9",
    To: "inquiries1424@gmail.com",
    From: "inquiries1424@gmail.com",
    Subject: 'Feedback'+name,
    Body: body
  }).then(
    message => {
      if (message == 'OK') {
        swal("Successful!", "Your Feedback Successfully Received!", "success");
        // Close the form
        document.getElementById('feedbackForm').style.display = 'none';
        // Clear input fields
        document.getElementById('name').value = '';
        document.getElementById('email').value = '';
        document.getElementById('feedback').value = '';
      } else {
        swal("Something Wrong", "Your Feedback is not Received!", "error");
      }
    }
  );
}