document.getElementById("choice").onclick = function sendData () {
    // (A) GET FORM DATA
    link = "http://127.0.0.1:8080/find?q=" + document.getElementById("Restaurant-Search").value
    console.log(link);
    fetchData(link)
    
    // (F) PREVENT FORM SUBMIT
    return false;
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
fetchData();