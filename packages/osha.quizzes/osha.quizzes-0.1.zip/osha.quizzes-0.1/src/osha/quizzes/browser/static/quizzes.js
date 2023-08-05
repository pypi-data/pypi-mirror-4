/*global $, document*/
(function () {
    "use strict";

    $(document).ready(function () {

        var overlayOpts = {
            subtype: "ajax",
            filter: "#content"
        };

        $("#quizzes-listing a.quiz-link").prepOverlay(overlayOpts);
    });

}());
