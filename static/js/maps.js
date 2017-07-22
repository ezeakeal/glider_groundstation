/* google maps -----------------------------------------------------*/
google.maps.event.addDomListener(window, 'load', initialize_map);

var map;
var infowindow;
var marker_obj = {};
var path_line;

function initialize_map() {
    console.log("Initializing map");
    var pos = {lat: 53.50932, lng: -6.52371};
    var mapOptions = {
        center: pos,
        zoom: 10
    };
    map = new google.maps.Map(document.getElementById("map_plot"), mapOptions);
    infowindow = new google.maps.InfoWindow({
        content: 'Empty'
    });
    setInterval(function(){
        google.maps.event.trigger(map, 'resize');
    }, 3000);

    $('.open-nav').click(open_directions);
};

function create_marker(callsign) {
    var new_marker = new google.maps.Marker({
        position: {lat: 0, lng: 0},
        url: '/',
        animation: google.maps.Animation.DROP,
        title: callsign,
        label: callsign[0],
        map: map
    });
    marker_obj[callsign] = new_marker;
    google.maps.event.addListener(new_marker, 'click', function() {
        infowindow.setContent(new_marker.info_content);
        infowindow.open(map, new_marker);
    });
}

function updateMapMarkers(all_data){
    // Hack to add target marker
    target_callsign = "TARGET";
    if (! marker_obj.hasOwnProperty(target_callsign))
        create_marker(target_callsign);

    var lat = all_data["glider"]['lat_target'];
    var lon = all_data["glider"]['lon_target'];

    var target_latlon = new google.maps.LatLng(
        lat, lon
    );
    marker_obj[target_callsign].setPosition(target_latlon);

    for (var callsign in all_data) {
        if (all_data.hasOwnProperty(callsign)) {
            if (! marker_obj.hasOwnProperty(callsign)){
                create_marker(callsign);
            }
            var lat = all_data[callsign]['lat'];
            var lon = all_data[callsign]['lon'];
            var alt = all_data[callsign]['alt'];
            var hhmmss = all_data[callsign]['hhmmss'];
            var time_received = all_data[callsign]['time_received'];
            var date = new Date(0); // The 0 there is the key, which sets the date to the epoch
            date.setUTCSeconds(time_received);

            var latlon = new google.maps.LatLng(
                lat, lon
            );

            html_content = "<h2>" + callsign + "</h2>";
            html_content += "<p>Received: " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds() + "</p>";
            html_content += "<p>HHMSS: " + hhmmss + "</p>";
            html_content += "<p>LAT: " + lat + "</p>";
            html_content += "<p>LON: " + lon + "</p>";
            html_content += "<p>ALT: " + alt + "</p>";
            marker_obj[callsign].info_content = html_content;
            marker_obj[callsign].setPosition(latlon );

            if (!path_line){
                path_line = new google.maps.Polyline({
                    path: [latlon , target_latlon],
                    strokeColor: "#00FF00",
                    strokeOpacity: 0.5,
                    strokeWeight: 3,
                    map: map
                });
            } else {
                path_line.setPath([latlon , target_latlon]);
            }
        }
    }

}

function open_directions(){
    var destination_type = $(this).data("dest");
    if (destination_type == "glider"){
        target = $('#lat').text() + "," + $('#lon').text();
    } else if (destination_type == "target"){
        target = $('#lat_target').text() + "," + $('#lon_target').text();
    }
    if (target == ","){
        alert("No coordinates found, check telemetry");
    } else {
        window.open('google.navigation:q=' + target + '&mode=d', '_system');
    }
}