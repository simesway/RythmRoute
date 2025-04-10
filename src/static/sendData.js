function search_genre() {
  // Get the value from the input field
  const name = document.getElementById('genre-query').value;
  console.log(name)

       if (name.trim() === "") {
        alert("Name cannot be empty!");
        return;
      }
  // Prepare the JSON data
  const data = {
    action: "expand",
    name: name
  };

  // Send the JSON to the backend API via POST request
  session.updateOnServer(data, '/api/graph/update')
}
