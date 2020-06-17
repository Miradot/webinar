<?php
$servername = "10.141.141.100";
$username = "test_user";
$password = "secretpwd";
$dbname = "test_db";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
echo "Database status...\n";
echo $conn->stat() . "\n";

$sql = "SELECT message FROM demo";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // output data of each row
    $i = 1;
    while($row = $result->fetch_assoc()) {
        echo "Row $i: " . $row["message"]. "\n";
        $i++;
    }
} else {
    echo "0 results";
}
$conn->close();
?>
