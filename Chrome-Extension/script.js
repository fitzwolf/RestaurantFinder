var lat = 0.0;
var long = 0.0;
document.getElementById("choice").onclick = function sendData () {
    // (A) GET FORM DATA
    link = "http://127.0.0.1:8080/find?q=" + document.getElementById("Restaurant-Search").value + "&latitude=" + lat + "&longitude=" + long
    console.log(link);
    fetchData(link)
    
    // (F) PREVENT FORM SUBMIT
    return false;
  }

var x = document.getElementById("loc");
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        x.innerHTML = "Unavailable.";
    }
}
function showPosition(position) {
    x.innerHTML = "Latitude: " + position.coords.latitude + 
    "<br>Longitude: " + position.coords.longitude;
    lat = position.coords.latitude;
    long = position.coords.longitude; 
}

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
        <td>${record[i].stars}</td>
      </tr>
      `
      table.innerHTML += row
    }
}
getLocation();
fetchData();