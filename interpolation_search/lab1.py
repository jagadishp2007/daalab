from flask import Flask, request, jsonify, render_template_string
import time
import random

app = Flask(__name__)

# ---------------- SEARCH ALGORITHMS ---------------- #

def interpolation_search(arr, target):
    low = 0
    high = len(arr) - 1
    comparisons = 0

    while low <= high and arr[low] <= target <= arr[high]:
        comparisons += 1

        if arr[low] == arr[high]:
            if arr[low] == target:
                return low, comparisons
            break

        pos = low + ((target - arr[low]) * (high - low)) // (arr[high] - arr[low])

        if arr[pos] == target:
            return pos, comparisons
        elif arr[pos] < target:
            low = pos + 1
        else:
            high = pos - 1

    return -1, comparisons


def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    comparisons = 0

    while low <= high:
        comparisons += 1
        mid = (low + high) // 2

        if arr[mid] == target:
            return mid, comparisons
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1, comparisons


# ---------------- PERFORMANCE ---------------- #

def performance_analysis():
    sizes = [1000, 5000, 10000, 50000, 100000]
    results = []

    for size in sizes:
        arr = sorted(random.sample(range(size * 10), size))
        target = arr[random.randint(0, size - 1)]

        start = time.perf_counter()
        for _ in range(100):
            _, comp_is = interpolation_search(arr, target)
        is_time = (time.perf_counter() - start) / 100 * 1000

        start = time.perf_counter()
        for _ in range(100):
            _, comp_bs = binary_search(arr, target)
        bs_time = (time.perf_counter() - start) / 100 * 1000

        results.append({
            "size": size,
            "interpolation_time_ms": round(is_time, 4),
            "binary_time_ms": round(bs_time, 4),
            "interpolation_comparisons": comp_is,
            "binary_comparisons": comp_bs
        })

    return results


# ---------------- HTML ---------------- #

HTML = """

<!DOCTYPE html>
<html>

<head>

<title>Interpolation Search Web Service</title>

<style>

body{
font-family:Arial;
background:#f0f2f5;
margin:0;
padding:40px;
}

.container{
width:750px;
margin:auto;
background:white;
padding:30px;
border-radius:10px;
box-shadow:0px 0px 10px gray;
}

h2{
text-align:center;
color:#007BFF;
}

label{
font-weight:bold;
}

input{
width:100%;
padding:10px;
margin-top:5px;
margin-bottom:15px;
font-size:16px;
}

button{
padding:10px 20px;
font-size:16px;
background:#007BFF;
color:white;
border:none;
border-radius:5px;
cursor:pointer;
margin-right:10px;
}

button:hover{
background:#0056b3;
}

table{
width:100%;
border-collapse:collapse;
margin-top:20px;
}

th{
background:#007BFF;
color:white;
padding:10px;
}

td{
padding:10px;
text-align:center;
}

table,th,td{
border:1px solid gray;
}

.result{
margin-top:20px;
background:#f8f8f8;
padding:15px;
border-radius:5px;
}

</style>

</head>

<body>

<div class="container">

<h2>Interpolation Search Web Service</h2>

<label>Enter Sorted Array (comma separated)</label>

<input id="array" placeholder="10,20,30,40,50">

<label>Enter Target Element</label>

<input id="target" type="number">

<button onclick="searchData()">Search</button>

<button onclick="performance()">Performance</button>

<div id="output" class="result"></div>

</div>

<script>

async function searchData(){

let arr=document.getElementById("array").value
.split(",")
.map(Number);

let target=parseInt(document.getElementById("target").value);

let response=await fetch("/search",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

array:arr,
target:target

})

});

let data=await response.json();

document.getElementById("output").innerHTML=`

<h3>Search Result</h3>

<table>

<tr>

<th>Algorithm</th>

<th>Index</th>

<th>Comparisons</th>

</tr>

<tr>

<td>Interpolation Search</td>

<td>${data.interpolation.index}</td>

<td>${data.interpolation.comparisons}</td>

</tr>

<tr>

<td>Binary Search</td>

<td>${data.binary.index}</td>

<td>${data.binary.comparisons}</td>

</tr>

</table>

`;

}


async function performance(){

let response=await fetch("/performance");

let data=await response.json();

let table=`

<h3>Performance Analysis</h3>

<table>

<tr>

<th>Size</th>

<th>IS Time (ms)</th>

<th>BS Time (ms)</th>

<th>IS Comparisons</th>

<th>BS Comparisons</th>

</tr>

`;

data.forEach(function(item){

table+=`

<tr>

<td>${item.size}</td>

<td>${item.interpolation_time_ms}</td>

<td>${item.binary_time_ms}</td>

<td>${item.interpolation_comparisons}</td>

<td>${item.binary_comparisons}</td>

</tr>

`;

});

table+="</table>";

document.getElementById("output").innerHTML=table;

}

</script>

</body>

</html>

"""

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/search", methods=["POST"])
def search():

    data = request.get_json()

    arr = data["array"]
    target = data["target"]

    idx1, comp1 = interpolation_search(arr, target)
    idx2, comp2 = binary_search(arr, target)

    return jsonify({
        "interpolation": {
            "index": idx1,
            "comparisons": comp1
        },
        "binary": {
            "index": idx2,
            "comparisons": comp2
        }
    })


@app.route("/performance")
def performance():
    return jsonify(performance_analysis())


if __name__ == "__main__":
    app.run(debug=True)