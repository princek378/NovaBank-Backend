import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";


function TransferMoney(){

    const navigate = useNavigate();

    const location = useLocation();



    const senderAccount =
    location.state?.account_number || "";



    const [receiverAccount, setReceiverAccount] = useState("");

    const [amount, setAmount] = useState("");

    const [message, setMessage] = useState("");

    const [loading, setLoading] = useState(false);





    async function transferMoney(){


        if(!receiverAccount || !amount){

            setMessage(
                "Enter receiver account and amount"
            );

            return;

        }



        setLoading(true);



        try{


            const response = await fetch(

                `${getApiUrl()}/api/transactions/transfer`,

                {

                    method:"POST",

                    headers:{

                        "Content-Type":
                        "application/json"

                    },


                    body:JSON.stringify({

                        from_account:
                        senderAccount,


                        to_account:
                        receiverAccount,


                        amount:
                        amount

                    })

                }

            );



            const data =
            await response.json();




            if(response.ok){


                setMessage(

                    "Transfer successful. New balance: $" +
                    data.sender_balance

                );


                setTimeout(()=>{


                    navigate(
                        "/customer/dashboard"
                    );


                },2000);


            }


            else{


                setMessage(
                    data.message
                );


            }



        }


        catch(error){


            console.log(error);


            setMessage(
                "Server error"
            );


        }


        finally{


            setLoading(false);


        }


    }







    return (

        <div className="transfer-page">


            <h1>
                Transfer Money
            </h1>





            <div className="transfer-card">



                <label>
                    Your Account
                </label>


                <input

                    value={senderAccount}

                    disabled

                />





                <label>
                    Receiver Account Number
                </label>


                <input

                    type="text"

                    placeholder="Enter receiver account"

                    value={receiverAccount}

                    onChange={
                        e =>
                        setReceiverAccount(
                            e.target.value
                        )
                    }

                />






                <label>
                    Amount
                </label>


                <input

                    type="number"

                    placeholder="Enter amount"

                    value={amount}

                    onChange={
                        e =>
                        setAmount(
                            e.target.value
                        )
                    }

                />






                <button

                onClick={transferMoney}

                disabled={loading}

                >

                    {

                    loading

                    ?

                    "Processing..."

                    :

                    "Transfer"

                    }


                </button>





                {
                message &&

                <p>

                    {message}

                </p>

                }





                <button

                onClick={()=>navigate(
                    "/customer/dashboard"
                )}

                >

                    Cancel

                </button>




            </div>


        </div>

    );

}


export default TransferMoney;