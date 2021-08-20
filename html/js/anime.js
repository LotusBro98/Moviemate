videoElement = document.getElementById("mainPlayer");

function get(name){
   if(name=(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search))
      return decodeURIComponent(name[1]);
}

function onPlay(e) {
    e.preventDefault();
    e.stopPropagation();

    $.ajax({
        url: "/api/party",
        data : {
            action: "play",
            sid: get("sid"),
            time: videoElement.currentTime
        },
        type: 'GET',
        success: function(res) {
            console.debug("Video played. Current time of videoplay: " + videoElement.currentTime );
        }
    });
}

function onPause(e) {
    e.preventDefault();
    e.stopPropagation();

    $.ajax({
        url: "/api/party",
        data : {
            action: "pause",
            sid: get("sid"),
            time: videoElement.currentTime
        },
        type: 'GET',
        success: function(res) {
            console.debug("Video paused. Current time of videoplay: " + videoElement.currentTime );
        }
    });
}

function requestUpdate() {
    $.ajax({
        url: "/api/party",
        data : {
            action: "update",
            sid: get("sid")
        },
        type: 'GET',
        success: function(res) {
            console.debug("Sent update request");
        }
    });
}

function listenAction(response) {
    var pr;
    var time;
    var next = true;

    try {
        console.log("Received message: " + JSON.stringify(response));
        for (let i = 0; i < response.length; i++) {
            let res = response[i];
            console.log("Handling action " + JSON.stringify(res));
            if (res.hasOwnProperty("action")) {
                if (res.action == "play") {
                    if (res.hasOwnProperty("time")) {
                        time = res.time;
                        time = parseFloat(time);
                        console.log("Setting time" + time);
                        try {
                            videoElement.currentTime = time;
                        } catch (e) {
                            console.error(e);
                        }
                    }

                    videoElement.removeEventListener('play', onPlay);
                    pr = videoElement.play();
                    pr.catch(function(error) {
                        console.log("Redirecting to " + window.location.href);
                        window.location.replace(window.location.href);
                    });
                    pr.then(function() {
                        videoElement.addEventListener('play', onPlay, true);
                    });

                    console.log("Playing");
                } else if (res.action == "pause") {

                    videoElement.removeEventListener('pause', onPause);
                    videoElement.pause();
                    videoElement.addEventListener('pause', onPause, true);

                    console.log("Pausing");
                    if (res.hasOwnProperty("time")) {
                        time = res.time;
                        time = parseFloat(time);
                        console.log("Setting time" + time);
                        try {
                            videoElement.currentTime = time;
                        } catch (e) {
                            console.error(e);
                        }
                    }
                } else if (res.action == "redirect") {
                    console.log("Redirecting to " + res.url);
                    next = false;
                    window.location.replace(res.url);
                }
            }
        }
    } catch (e) {
        console.error(e);
    }

    if (next)
        listen();
}

async function listen() {
    console.debug("Listening");
    $.ajax({
        url: "/api/party",
        data: {
            action: "listen",
            sid: get("sid"),
            anime: get("anime"),
            ep: get("ep")
        },
        type: 'GET',
        success: listenAction,
        error: function (res) {
            listen()
        }
    });
}

function inviteUser(user_id) {
    $.ajax({
        url: "/api/party",
        data : {
            action: "invite",
            sid: get("sid"),
            user_id: user_id
        },
        type: 'GET',
        success: function(res) {
            console.debug("Sent invite request to " + user_id);
        }
    });
}

function joinParty(party_id) {
    $.ajax({
        url: "/api/party",
        data : {
            action: "join",
            sid: get("sid"),
            party: party_id
        },
        type: 'GET',
        success: function(res) {
            console.debug("Joined " + party_id);
        }
    });
}

function leaveParty() {
    $.ajax({
        url: "/api/party",
        data : {
            action: "leave",
            sid: get("sid")
        },
        type: 'GET',
        success: function(res) {
            console.debug("Left party");
        }
    });
}

function createParty() {
    $.ajax({
        url: "/api/party",
        data : {
            action: "create",
            sid: get("sid")
        },
        type: 'GET',
        success: function(res) {
            console.debug("Created party");
        }
    });
}

function changeAnime(anime_id, episode_id) {
    $.ajax({
        url: "/api/party",
        data : {
            action: "change",
            sid: get("sid"),
            anime: anime_id,
            episode: episode_id
        },
        type: 'GET',
        success: function(res) {
            console.debug("Created party");
        }
    });
}
