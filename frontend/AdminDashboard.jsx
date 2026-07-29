import { useEffect, useState } from "react";

console.log("NEW ADMIN DASHBOARD LOADED");

export default function AdminDashboard(){


const [stats,setStats] = useState(null);



useEffect(()=>{


fetch(
"http://127.0.0.1:5000/api/admin/stats"
)

.then(res=>res.json())

.then(data=>{

console.log(data);

setStats(data);

})


.catch(error=>{

console.log(error);

});


},[]);




return (

<div>


<h1>
NovaBank Admin Dashboard
</h1>


<h2>
Welcome Administrator
</h2>



{
stats ?


<div>


<h3>
Customers:
{stats.customers}
</h3>


<h3>
Accounts:
{stats.accounts}
</h3>


<h3>
Transactions:
{stats.transactions}
</h3>


<h3>
Total Bank Balance:
${stats.total_balance}
</h3>


</div>



:


<h3>
Loading statistics...
</h3>


}



</div>


);


}