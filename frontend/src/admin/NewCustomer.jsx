import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

import "./NewCustomer.css";



export default function NewCustomer(){


const navigate = useNavigate();




const [form,setForm] = useState({

    first_name:"",

    last_name:"",

    email:"",

    password:"",

    phone:"",

    country:"",

    address:"",

    account_type:"Savings",

    balance:"0"

});







function handleChange(e){


    setForm({

        ...form,

        [e.target.name]:

        e.target.value

    });


}










async function createCustomer(e){


e.preventDefault();




try{


const response = await fetch(

`${getApiUrl()}/api/admin/customers`,

{

method:"POST",

headers:{


"Content-Type":

"application/json"


},


body:JSON.stringify(form)


}

);






const data = await response.json();






if(response.ok){


alert(

"Customer Created Successfully!\n\nAccount Number: "

+

data.account_number

);




navigate(

"/admin/customers"

);



}

else{


alert(

data.message

);


}





}

catch(error){


console.log(error);


alert(

"Server connection failed"

);


}



}









return(


<div className="admin-layout">


<Sidebar/>





<div className="main-content">


<Topbar/>






<div className="new-customer-header">


<h1>

Create New Customer

</h1>



<p>

Register a new NovaBank customer account

</p>



</div>










<form

className="customer-form"

onSubmit={createCustomer}

>





<div className="form-section">


<h2>

👤 Personal Information

</h2>







<div className="form-grid">





<input

name="first_name"

placeholder="First Name"

value={form.first_name}

onChange={handleChange}

required

/>





<input

name="last_name"

placeholder="Last Name"

value={form.last_name}

onChange={handleChange}

required

/>







<input

name="email"

type="email"

placeholder="Email Address"

value={form.email}

onChange={handleChange}

required

/>







<input

name="password"

type="password"

placeholder="Password"

value={form.password}

onChange={handleChange}

required

/>







<input

name="phone"

placeholder="Phone Number"

value={form.phone}

onChange={handleChange}

/>








<input

name="country"

placeholder="Country"

value={form.country}

onChange={handleChange}

/>







<input

className="full-input"

name="address"

placeholder="Home Address"

value={form.address}

onChange={handleChange}

/>





</div>



</div>









<div className="form-section">


<h2>

💳 Account Information

</h2>






<div className="form-grid">






<select

name="account_type"

value={form.account_type}

onChange={handleChange}

>


<option value="Savings">

Savings Account

</option>



<option value="Current">

Current Account

</option>



<option value="Business">

Business Account

</option>


</select>








<input

name="balance"

type="number"

placeholder="Opening Balance"

value={form.balance}

onChange={handleChange}

/>





</div>



</div>









<button

className="create-btn"

type="submit"

>


Create Customer Account


</button>







</form>







</div>



</div>


);


}