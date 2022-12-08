// script to handle user interaction on the extension
// on extension load, we get user's location and add click event listeners for 'Go' and 'Clear' button
// when user enters the search query (like restaurants with outdoor seating) and clicks on 'Go', 
// data is fetched from the restaurant finder app which is running in the background
// for the UI, this app uses bootstrap framework

let lat;
let long;
const appUrl = "http://127.0.0.1:8080"
const findApiPath = "/find"

const fullStar = `
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">
  <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>
</svg>
`
const halfStar = `
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-half" viewBox="0 0 16 16">
  <path d="M5.354 5.119 7.538.792A.516.516 0 0 1 8 .5c.183 0 .366.097.465.292l2.184 4.327 4.898.696A.537.537 0 0 1 16 6.32a.548.548 0 0 1-.17.445l-3.523 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256a.52.52 0 0 1-.146.05c-.342.06-.668-.254-.6-.642l.83-4.73L.173 6.765a.55.55 0 0 1-.172-.403.58.58 0 0 1 .085-.302.513.513 0 0 1 .37-.245l4.898-.696zM8 12.027a.5.5 0 0 1 .232.056l3.686 1.894-.694-3.957a.565.565 0 0 1 .162-.505l2.907-2.77-4.052-.576a.525.525 0 0 1-.393-.288L8.001 2.223 8 2.226v9.8z"/>
</svg>
`
const emptyStar = `
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star" viewBox="0 0 16 16">
  <path d="M2.866 14.85c-.078.444.36.791.746.593l4.39-2.256 4.389 2.256c.386.198.824-.149.746-.592l-.83-4.73 3.522-3.356c.33-.314.16-.888-.282-.95l-4.898-.696L8.465.792a.513.513 0 0 0-.927 0L5.354 5.12l-4.898.696c-.441.062-.612.636-.283.95l3.523 3.356-.83 4.73zm4.905-2.767-3.686 1.894.694-3.957a.565.565 0 0 0-.163-.505L1.71 6.745l4.052-.576a.525.525 0 0 0 .393-.288L8 2.223l1.847 3.658a.525.525 0 0 0 .393.288l4.052.575-2.906 2.77a.565.565 0 0 0-.163.506l.694 3.957-3.686-1.894a.503.503 0 0 0-.461 0z"/>
</svg>
`

function getRatingStars(stars) {
  if (stars === undefined) {
    return ''
  }

  fullStarCount = Math.floor(stars)
  halfStarCount = 0
  if (stars - fullStarCount === 0.5) {
    halfStarCount = 1
  }
  emptyStarsCount = 5 - fullStarCount - halfStarCount
  return fullStar.repeat(fullStarCount) + halfStar.repeat(halfStarCount) + emptyStar.repeat(emptyStarsCount)
}

function getGoogleSearchUrl(name, city, state) {
  return `https://www.google.com/search?q=${name}+${city}+${state}`
}

async function getCurrentTab() {
  let [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
  return tab;
}

function getNearestRestaurantElement(restaurantList) {
  nearestElement = ''
  restaurantList.forEach(restaurant => {
    if (restaurant.nearest !== undefined && restaurant.nearest === true) {
      nearestElement = `<div><em>Nearest restaurant: ${restaurant.city}, ${restaurant.state}</em></div>`
    }
  });
  return nearestElement;
}

// get search results
async function fetchData(link) {
  const res = await fetch(link, {
    method: 'GET',
    headers: {
      accept: 'application/json',
    },
  });

  if (!res.ok) {
    throw new Error('ERROR: status: ${res.status} ')
  }

  const restaurantList = await res.json();
  table = document.getElementById('search-results')
  table.innerHTML = `
    <table class="col table table-light table-hover caption-top mb-0">
      <caption class="p-2">
        <div><small>Search results<small></div>
        ${getNearestRestaurantElement(restaurantList)}
      </caption>
      <tbody id="restaurant-list"></tbody>
    </table>
  `;
  tableBody = document.getElementById('restaurant-list')
  restaurantList.forEach(restaurant => {
    tableBody.innerHTML += `
    <tr>
      <td>
        <div>
          <strong><a class="btn btn-link p-0" href="https://www.google.com/search?q=${restaurant.name}+${restaurant.city}+${restaurant.state}" role="button" id="restaurant-link-${restaurantList.indexOf(restaurant)}">${restaurant.name}</a></strong>
        </div>
        <div>${restaurant.address}</div>
        <div>${restaurant.city}, ${restaurant.state} ${restaurant.postal_code}</div>
        <div>${getRatingStars(restaurant.stars)}</div>
      </td>
    </tr>
    `
  });

  // event listener for each restaurant link
  restaurantList.forEach(restaurant => {
    document.getElementById(`restaurant-link-${restaurantList.indexOf(restaurant)}`).onclick = () => {
      chrome.tabs.update(getCurrentTab().id, { url: getGoogleSearchUrl(restaurant.name, restaurant.city, restaurant.state) });
      return false;
    }
  })
}


// event listener for 'Go' button
document.getElementById("go").onclick = () => {
  link = appUrl + findApiPath + "?q=" + document.getElementById("user-query").value

  if (lat !== undefined && long !== undefined) {
    link += "&latitude=" + lat + "&longitude=" + long
  }

  fetchData(link)
  // prevent form submit
  return false;
}

// event listener for 'Clear' button
document.getElementById("clear-results").onclick = () => {
  userInput = document.getElementById("user-query")
  userInput.innerHTML = ""
  table = document.getElementById("search-results")
  table.innerHTML = ""
  return false;
}

// get user location
function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((position) => {
      lat = position.coords.latitude;
      long = position.coords.longitude;
    });
  }
}

getLocation();
