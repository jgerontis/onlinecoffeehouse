var posts = null;
var BASE_URL = "https://onlinecoffeehouse.herokuapp.com";

function deletePostFromServer(PostId){
  fetch(BASE_URL + "/posts/"+PostId, {
    method: "DELETE",
    credentials: "include" // DO EVERYWHERE WE CALL A METHOD
  }).then(function (response) {
    loadPosts();
  });
}

function editPost(post){

  var newMessageText = document.getElementById(post["id"]).value;


  console.log(post["id"]);
  var PostId = post["id"];
  var postFName = post["firstName"];
  var postLName = post["lastName"];
  var postMessage = newMessageText;
  var postLocation = post["location"]
  var postDate = new Date();

  var data = "fName=" + encodeURIComponent(postFName);
  data += "&lName=" + encodeURIComponent(postLName);
  data += "&message=" + encodeURIComponent(postMessage);
  data += "&location=" + encodeURIComponent(postLocation);
  data += "&date=" + encodeURIComponent(postDate);

  console.log(newMessageText);

  // 3. PUT, send data to server
  fetch(BASE_URL + "/posts/"+PostId, {
    method: "PUT",
    credentials: "include",
    body: data,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  }).then(function (response) {
    if (!response.ok){
      throw new Error('Oh boy we had an error, check the console for details.');
    } else {
      loadPosts();
    }
  }).catch((error) => {
    console.error('There has been a problem with your fetch operation:', error);
  });

}

// login/register display stuff

var loginAndRegisterField = document.getElementById("loginAndRegister");
var contentUl = document.getElementById("content");
var createArea = document.getElementById("createArea");
var loginFields = document.getElementById("loginFields");
var regFields = document.getElementById("regFields");
var loginButton = document.getElementById("loginButton");
var registerButton = document.getElementById("registerButton");
var loginSubmitButton = document.getElementById("loginSubmit");
var registerSubmitButton = document.getElementById("regSubmit");



loginButton.onclick = function () {
  loginFields.style.display = "block";
  regFields.style.display = "none";
}

registerButton.onclick = function () {
  regFields.style.display = "block";
  loginFields.style.display = "none";
}



// login
loginSubmitButton.onclick = function () {
  // capture login data
  var logineMail = document.querySelector("#loginEmailField").value;
  var loginPassword = document.querySelector("#loginPasswordField").value;

  // encode data
  var data = "email=" + encodeURIComponent(logineMail);
  data += "&password=" + encodeURIComponent(loginPassword);

  // fetch (POST): send data to server
  fetch(BASE_URL + "/sessions", {
    method: "POST",
    credentials: "include",
    body: data,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  }).then(function (response) {
    if (!response.ok){
      throw new Error('Oh boy we had an error, check the console for details.');
    } else {
      loadPosts();
    }
  }).catch((error) => {
    console.error('Error logging in:', error);
    alert("Log in unsuccessful, username/password incorrect.");
  });
}


// register
registerSubmitButton.onclick = function () {
  // capture data from text fields
  var regfName = document.querySelector("#regFirstNameField").value;
  var reglName = document.querySelector("#regLastNameField").value;
  var regeMail = document.querySelector("#regEmailField").value;
  var regPass  = document.querySelector("#regPasswordField").value;
  
  // encode the data (url encoded)
  var data = "firstName=" + encodeURIComponent(regfName);
  data += "&lastName=" + encodeURIComponent(reglName);
  data += "&email=" + encodeURIComponent(regeMail);
  data += "&password=" + encodeURIComponent(regPass);

  // fetch (POST): send data to server
  fetch(BASE_URL + "/users", {
    method: "POST",
    credentials: "include",
    body: data,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  }).then(function (response) {
    if (!response.ok){
      throw new Error('Oh boy we had an error, check the console for details.');
    } else {
      confirm("Registration Successful! Please login.");
    }
  }).catch((error) => {
    console.error('There has been a problem with your fetch operation:', error);
    alert("User already exists with that email, please try again.");
  });
}




var addButton = document.getElementById("addButton");

addButton.onclick = function () {
  // TODO: send the new post to the server
  // 1. capture text from input field
  var postfNameInput = document.querySelector("#post-fName");
  var postFName = postfNameInput.value;
  var postLNameInput = document.querySelector("#post-lName");
  var postLName = postLNameInput.value;
  var postMessageInput = document.querySelector("#post-message");
  var postMessage = postMessageInput.value;
  var postLocationInput = document.querySelector("#post-location");
  var postLocation = postLocationInput.value;
  var postDate = new Date();
  //var message = messageInput.value;
  console.log("You entered:", postFName, postLName, postMessage, postLocation);

  // 2. encode the data (url encoded)
  //var data = "message=" + encodeURIComponent(message);
  var data = "fName=" + encodeURIComponent(postFName);
  data += "&lName=" + encodeURIComponent(postLName);
  data += "&message=" + encodeURIComponent(postMessage);
  data += "&location=" + encodeURIComponent(postLocation);
  data += "&date=" + encodeURIComponent(postDate);

  // 3. fetch (POST): send data to server
  fetch(BASE_URL + "/posts", {
    method: "POST",
    credentials: "include",
    body: data,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  }).then(function (response) {
    if (!response.ok){
      throw new Error('Oh boy we had an error, check the console for details.');
    } else {
      loadPosts();
    }
  }).catch((error) => {
    console.error('There has been a problem with your fetch operation:', error);
  });
}

function loadPosts () {
    fetch(BASE_URL + "/posts", {
          credentials: "include"
          }).then(function (response) {
          if (response.status == 200) {
            contentUl.style.display = "block";
            createArea.style.display = "block";
            loginAndRegisterField.style.display = "none";
          } else if (response.status == 401){
            contentUl.style.display = "none";
            createArea.style.display = "none";
            loginAndRegisterField.style.display = "block";
            return;
          } else {
            return;
          }
          response.json().then(function (postsFromServer) {
            // data now ready: loop over posts & add to DOM
            posts = postsFromServer;
      
            var postsList = document.querySelector("#content");
            postsList.innerHTML = "";
            posts.forEach(function (post) {
              var descriptorText = "";
              var descriptorTextHolder = document.createElement("div");
              var listItem = document.createElement("li");
      
              var fName = post["firstName"];
              descriptorText += fName + " ";
      
              var lName = post["lastName"];
              descriptorText += lName + " from ";
      
              var location = post["location"];
              descriptorText += location + " says: ";
      
              descriptorTextHolder.innerHTML = descriptorText;
              listItem.appendChild(descriptorTextHolder);
      
              var messageEl = document.createElement("p");
              messageEl.innerHTML = post["message"];
              messageEl.classList.add("message");
              listItem.appendChild(messageEl);
      
              var dateEl = document.createElement("div");
              dateEl.innerHTML = post["date"];
              dateEl.classList.add("date");
              listItem.appendChild(dateEl);
      
              var editButton = document.createElement("button");
              editButton.innerHTML = "Edit";
              editButton.onclick = function() {
                  console.log("you clicked me.", post);

                  var editMessageField = document.createElement("input");
                  editMessageField.setAttribute("type","text");
                  editMessageField.setAttribute("value", post["message"]);
                  editMessageField.setAttribute("class","editField");
                  editMessageField.setAttribute("id", post["id"]);
                  listItem.appendChild(editMessageField)

                  var editSubmitButton = document.createElement("input");
                  editSubmitButton.setAttribute("type","submit");
                  editSubmitButton.setAttribute("value","Confirm");
                  listItem.appendChild(editSubmitButton);

                  editSubmitButton.onclick = function () {
                    editPost(post);
                    listItem.removeChild(editMessageField);
                    listItem.removeChild(editSubmitButton);
                  }
              };
              listItem.appendChild(editButton);
      
              var deleteButton = document.createElement("button");
              deleteButton.innerHTML = "Delete";
              deleteButton.onclick = function () {
                console.log("you clicked me.", post);
                if (confirm("Are you sure you want to delete " + post["firstName"] + "'s post?")) {
                  deletePostFromServer(post["id"]);
                }
              };
            listItem.appendChild(deleteButton);
      
            postsList.appendChild(listItem);
            });
      
          });
  });
}

loadPosts();



