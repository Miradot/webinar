<html>
    <head>
        <title>Miradot World Engine - LAMP</title>
        <link rel="stylesheet" href="bootstrap.min.css">
        <script type="text/javascript">
function loader() {
    console.log("Start");
    
    // Make the output div visible by removing the class that hides it.
    var elem = document.getElementById("dbcard")
    if (elem == null) {
        alert("Failed to find output element");
        console.log("Failed to find output element");
        return;
    }
    elem.classList.remove('d-none')

    // Element where we'll print the output.
    elem = document.getElementById("dboutput");
    if (elem == null) {
        alert("Failed to find output element");
        console.log("Failed to find output element");
        return;
    }
    var req = new XMLHttpRequest;
    req.onerror = function(event) {
        elem.textContent = "Error: http request failed.";
        console.log("Request failed!");
    };

    req.onreadystatechange = function () {
        console.log("-- stateChanged --");
        console.log(req.readyState);
        elem.textContent = "Sending query...";
        switch(req.readyState) {
        case 4:
            elem.textContent += "done\n";
            elem.textContent += req.responseText;
            break;
        }
        window.scrollTo(0,document.body.scrollHeight);
        console.log("-- end of stateChanged --");
    }

    req.open("GET","/querydb.php", true);
    req.send();

    console.log("Finished");
}
        </script>
    </head>
    <body class="bg-light">
        <div class="p-3">
            <img src="miradot.png" height="62px" width="285px" alt="Miradot - Viability through knowledge">
        </div>
        <div class="position-relative p-3 p-md-5 m-md-3 text-center">
            <div class="p-lg-5 mx-auto my-5">
                <img src="CiscoDevNet2.png" width="683px" height="233px" alt="Cisco DevNet">
                
                <h1 class="display-4 font-weight-normal">INFRASTRUCTURE AS CODE DEMO</h1>
                <p class="lead font-weight-normal">
                    <?php echo $_SERVER['SERVER_SOFTWARE']; ?><br>
                    <?php echo $_SERVER['SERVER_ADDR']; ?>:<?php echo $_SERVER['SERVER_PORT']; ?><br>
                </p>
                <a class="btn btn-outline-primary" href="javascript:loader();">Test database connection</a>
            </div>
        </div>
        <div class="card d-none p-3" id="dbcard">
            <p class="text-left" id="dboutput" style="font-size:1.1em;white-space:pre;"></p>
        </div>
    </body>
</html>
