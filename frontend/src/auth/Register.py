import {useState} from "react";
import axios from "axios";


export default function Register(){


const [form,setForm]=useState({

first_name:"",
last_name:"",
email:"",
password:""

});



function handleChange(e){

setForm({

...form,

[e.target.name]:
e.target.value

});

}



async function submit(e){

e.preventDefault();


try{


const response = await axios.post(

"http://127.0.0.1:5000/api/register",

form

);


alert(response.data.message);



}

catch(error){

alert(
"Registration failed"
);

}


}



return(

<div className="auth-container">


<h1>
Create NovaBank Account
</h1>



<form onSubmit={submit}>


<input

name="first_name"

placeholder="First Name"

onChange={handleChange}

/>


<input

name="last_name"

placeholder="Last Name"

onChange={handleChange}

/>


<input

name="email"

placeholder="Email"

type="email"

onChange={handleChange}

/>



<input

name="password"

placeholder="Password"

type="password"

onChange={handleChange}

/>



<button>

Create Account

</button>



</form>


</div>

)

}