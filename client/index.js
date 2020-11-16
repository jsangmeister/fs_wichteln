$(() => {
    var email = $("#email");
    var button = $("#button");
    button.click(() => {
        var val = email.val();
        if (email.is(':valid') && val.match(/^[a-z]+@uos.de$/)) {
            $.ajax({
                url: 'http://localhost:5000/request',
                type: 'POST',
                data: JSON.stringify({email: val}),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                async: false,
            }).done(function() {
                $("body").html("Du hast deine Daten per Email erhalten!");
            })
            .fail(function(_, status, error) {
                console.log(status);
                console.log(error);
                $("body").html("Ein Fehler ist aufgetreten: " + status + "; " + error);
            });
        } else {
            $("body").html("Ungültige Email-Adresse");
        }
    });
});
