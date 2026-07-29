import { useEffect, useState } from "react";
import { getApiUrl } from "../utils/api";
import axios from "axios";

import { Line } from "react-chartjs-2";

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement
} from "chart.js";


ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement
);



export default function Dashboard(){


    const [account,setAccount] = useState(null);

    const [transactions,setTransactions] = useState([]);



    useEffect(()=>{


        axios.get(
            `${getApiUrl()}/api/account`
        )
        .then((response)=>{

            setAccount(response.data);

        })
        .catch((error)=>{

            console.log(error);

        });



        axios.get(
            `${getApiUrl()}/api/transactions`
        )
        .then((response)=>{

            setTransactions(response.data);

        })
        .catch((error)=>{

            console.log(error);

        });



    },[]);




    const chartData = {

        labels:[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun"
        ],


        datasets:[

            {

                label:"Monthly Spending",

                data:[
                    300,
                    500,
                    200,
                    700,
                    400,
                    600
                ],


                borderWidth:3

            }

        ]

    };





    return(

        <div className="dashboard">


            <h1>
                Welcome Back 👋
            </h1>



            <div className="dashboard-grid">



                <div className="balance-card">


                    <p>
                        Available Balance
                    </p>


                    <h2>

                    {
                        account
                        ?
                        "$" + account.balance
                        :
                        "Loading..."
                    }

                    </h2>



                    <span>

                    {
                        account
                        ?
                        account.account_number
                        :
                        ""
                    }

                    </span>


                </div>





                <div className="info-card">


                    <h3>
                        Account Information
                    </h3>


                    <p>
                        Type:
                        {
                            account
                            ?
                            account.account_type
                            :
                            "Loading..."
                        }
                    </p>



                    <p>
                        Status:
                        {
                            account
                            ?
                            account.status
                            :
                            "Loading..."
                        }
                    </p>



                    <p>
                        Currency: USD
                    </p>


                </div>


            </div>





            <div className="chart-box">


                <h2>
                    Spending Overview
                </h2>


                <Line data={chartData}/>


            </div>





            <div className="transactions">


                <h2>
                    Recent Transactions
                </h2>



                {

                    transactions.map(
                        (item,index)=>(

                            <div 
                            className="transaction"
                            key={index}
                            >


                                <p>
                                    {item.name}
                                </p>



                                <strong>
                                    {item.amount}
                                </strong>


                            </div>

                        )

                    )

                }



            </div>



        </div>

    )


}