// The general idea of this whole app is to take a collection of 
// reviews - in this sample we are using Yelp's academic dataset -
// and from those reviews then all the users to ask for more detailed
// information such as restaurants that have a cozy environment.
// to accomplish this there are several steps. The first is to turn
// the dataset into an index using dataset.py then start up the
// app.py which will make a local webserver that defaults
// to port 8080. This port will then be communicated to by either
// either directly accessing index.html or through the chrome-extension
// titled RestaurantFinder.
// index.html builds a table and has a search textfield that triggers
// in thie file: sendData() which in turn uses fetchData to send the
// query and then take the returned results and parse out the
// restaurant name, address, city and stars and display them
// into the table in index.html. By default the code will also
// get the user's location and use that as part of the search


// lat and long are used to store the user's latitude and longitude
var lat = 0.0;
var long = 0.0;
// this function is triggered when the user clicks Go on the index.html
document.getElementById("choice").onclick = function sendData () {
    // (A) GET FORM DATA - this needs to be modified if you change the
    // default url
    link = "http://127.0.0.1:8080/find?q=" + document.getElementById("Restaurant-Search").value + "&latitude=" + lat + "&longitude=" + long
    console.log(link);
    fetchData(link)
    
    // (F) PREVENT FORM SUBMIT
    return false;
  }

  // this script gets the user location (lat and long)
var x = document.getElementById("loc");
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        x.innerHTML = "Unavailable.";
    }
}
function showPosition(position) {
    x.innerHTML = "This search is using your default location of Latitude: " + position.coords.latitude + 
    " and Longitude: " + position.coords.longitude + 
    ".<br> But because the academic dataset is small" +
    " some results might be further away than expected.";
    lat = position.coords.latitude;
    long = position.coords.longitude; 
}

// this function retrieves the data from the search and appends it to the table
// for easy viewing.
async function fetchData(link) {
    const res=await fetch (link, {
      method: 'GET',
      headers: {
        accept: 'application/json',
      },
    });
    if (!res.ok) {
      throw new Error('Error! status: ${res.status} ')
    }
    const record=await res.json();
    console.log(record)
    table = document.getElementById('RestaurantTable')
    table.innerHTML = "";
    for (var i = 0; i< record.length; i++)
    {
      var row = `<tr>
        <td>${record[i].name}</td>
        <td>${record[i].address}</td>
        <td>${record[i].city}</td>
        <td>${record[i].stars}</td>
      </tr>
      `
      table.innerHTML += row
    }
}
getLocation();
fetchData();