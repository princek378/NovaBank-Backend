import { useEffect, useState } from "react";
import { getApiUrl } from "../utils/api";

import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    PieChart,
    Pie,
    Cell
} from "recharts";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

import "./Reports.css";



export default function Reports(){


const [report,setReport] = useState({

    customers:0,

    accounts:0,

    balance:0,

    deposits:0,

    withdrawals:0,

    transfers:0,

    messages:0

});


const [loading,setLoading] = useState(true);



const [error,setError] = useState("");





useEffect(()=>{

    loadReport();

},[]);







async function loadReport(){


try{


const response = await fetch(

`${getApiUrl()}/api/admin/reports`

);



if(!response.ok){

throw new Error(
"Failed to load reports"
);

}



const data = await response.json();



setReport(data);



}

catch(err){


console.log(err);


setError(
"Unable to connect to banking server"
);


}

finally{


setLoading(false);


}


}







const barData=[


{

name:"Deposits",

value:Number(report.deposits)

},


{

name:"Withdrawals",

value:Number(report.withdrawals)

},


{

name:"Transfers",

value:Number(report.transfers)

}


];








const pieData=[


{

name:"Customers",

value:Number(report.customers)

},


{

name:"Accounts",

value:Number(report.accounts)

}


];








const COLORS=[

"#38bdf8",

"#22c55e"

];








if(loading){


return(

<div className="admin-layout">


<Sidebar/>


<div className="main-content">


<Topbar/>


<div className="loading-box">

Loading reports...

</div>


</div>


</div>

);


}










return(


<div className="admin-layout">


<Sidebar/>




<div className="main-content">


<Topbar/>





<div className="reports-header">


<h1>

📊 NovaBank Reports

</h1>


<p>

Bank performance analytics and transaction statistics

</p>


</div>









{

error &&

<div className="error-box">

{error}

</div>

}









<div className="report-cards">





<div className="report-card">

<h3>

👥 Customers

</h3>

<h1>

{report.customers}

</h1>

</div>






<div className="report-card">

<h3>

💳 Accounts

</h3>

<h1>

{report.accounts}

</h1>

</div>







<div className="report-card">

<h3>

🏦 Balance

</h3>

<h1>

{'$' + Number(report.balance).toLocaleString()}

</h1>

</div>







</div>









<div className="charts-grid">





<div className="chart-card">


<h2>

Transaction Overview

</h2>




<ResponsiveContainer

width="100%"

height={350}

>


<BarChart data={barData}>


<CartesianGrid strokeDasharray="3 3"/>


<XAxis dataKey="name"/>


<YAxis/>


<Tooltip/>




<Bar

dataKey="value"

fill="#38bdf8"

radius={[8,8,0,0]}

/>



</BarChart>



</ResponsiveContainer>



</div>









<div className="chart-card">


<h2>

Customers vs Accounts

</h2>



<ResponsiveContainer

width="100%"

height={350}

>



<PieChart>


<Pie

data={pieData}

dataKey="value"

outerRadius={120}

label

>


{

pieData.map((entry,index)=>(


<Cell

key={index}

fill={COLORS[index]}

/>


))

}



</Pie>


<Tooltip/>


</PieChart>



</ResponsiveContainer>



</div>






</div>









<div className="report-summary">





<div className="summary-box">


<h2>

💰 Deposits

</h2>


<h1>

{'$' + Number(report.deposits).toLocaleString()}

</h1>


</div>








<div className="summary-box">


<h2>

💸 Withdrawals

</h2>


<h1>

{'$' + Number(report.withdrawals).toLocaleString()}

</h1>


</div>









<div className="summary-box">


<h2>

🔄 Transfers

</h2>


<h1>

{'$' + Number(report.transfers).toLocaleString()}

</h1>


</div>





</div>







</div>



</div>


);


}