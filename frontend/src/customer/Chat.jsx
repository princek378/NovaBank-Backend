import { useEffect, useState } from "react";
import { getApiUrl } from "../utils/api";

import "./Chat.css";


export default function Chat(){


const [customer,setCustomer] = useState(null);

const [messages,setMessages] = useState([]);

const [message,setMessage] = useState("");

const [loading,setLoading] = useState(true);





useEffect(()=>{


loadProfile();


},[]);








async function loadProfile(){


try{


const token = localStorage.getItem("token");


const response = await fetch(

`${getApiUrl()}/api/customer/profile`,

{

headers:{

Authorization:`Bearer ${token}`

}

}

);



const data = await response.json();



setCustomer(data);



loadMessages(data.id);



}


catch(error){


console.log(error);


}



}









async function loadMessages(id){


try{


const response = await fetch(

`http://127.0.0.1:5000/api/chat/${id}`

);



const data = await response.json();



setMessages(data);



}


catch(error){


console.log(error);


}


finally{


setLoading(false);


}



}









async function sendMessage(){


if(!message.trim() || !customer)

return;






await fetch(

`${getApiUrl()}/api/chat/send`,

{


method:"POST",


headers:{


"Content-Type":"application/json"


},


body:JSON.stringify({


user_id:customer.id,


sender:"Customer",


message:message


})


}

);





setMessage("");



loadMessages(customer.id);



}








return(


<div className="customer-chat">





<h1>

💬 NovaBank Support

</h1>






<div className="chat-container">





<div className="chat-messages">



{

loading ?


<h3>

Loading messages...

</h3>


:


messages.length===0 ?


<p>

No conversation yet. Send us a message.

</p>



:


messages.map(msg=>(



<div


key={msg.id}


className={

msg.sender==="Customer"

?

"my-message"

:

"admin-message"

}


>


<p>

{msg.message}

</p>


<span>

{msg.sender}

</span>


</div>



))


}



</div>









<div className="chat-input">


<input


placeholder="Type your message..."


value={message}


onChange={(e)=>
setMessage(e.target.value)
}


/>



<button

onClick={sendMessage}

>

Send

</button>



</div>






</div>





</div>


);


}