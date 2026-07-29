import { useEffect, useState } from "react";
import { getApiUrl } from "../utils/api";


function Customers(){

    const [customers, setCustomers] = useState([]);

    const [search, setSearch] = useState("");



    useEffect(()=>{

        fetchCustomers();

    },[]);



    function fetchCustomers(){

        fetch(
            `${getApiUrl()}/api/admin/customers`
        )

        .then(response => response.json())

        .then(data => {

            setCustomers(data);

        })

        .catch(error => {

            console.log(
                "Error loading customers:",
                error
            );

        });

    }



    function freezeCustomer(id){


        fetch(
            `http://127.0.0.1:5000/api/admin/customers/${id}/freeze`,
            {
                method:"PUT"
            }
        )

        .then(()=>{

            fetchCustomers();

        });


    }



    function unfreezeCustomer(id){


        fetch(
            `http://127.0.0.1:5000/api/admin/customers/${id}/unfreeze`,
            {
                method:"PUT"
            }
        )

        .then(()=>{

            fetchCustomers();

        });


    }



    function deleteCustomer(id){


        const confirmDelete =
        window.confirm(
            "Are you sure you want to delete this customer?"
        );


        if(!confirmDelete)
            return;



        fetch(
            `http://127.0.0.1:5000/api/admin/customers/${id}`,
            {
                method:"DELETE"
            }
        )

        .then(()=>{

            fetchCustomers();

        });


    }



    const filteredCustomers =
    customers.filter(customer =>

        customer.name
        ?.toLowerCase()
        .includes(
            search.toLowerCase()
        )

    );



    return (

        <div className="customers-page">


            <h1>
                Customer Management
            </h1>



            <input

                type="text"

                placeholder="Search customers..."

                value={search}

                onChange={
                    (e)=>setSearch(e.target.value)
                }

                className="search-box"

            />



            <div className="customer-grid">


                {
                filteredCustomers.length === 0

                ?

                <h3>
                    No customers found
                </h3>

                :

                filteredCustomers.map(customer => (


                    <div
                    className="customer-card"
                    key={customer.id}
                    >


                        <h2>
                            {customer.name}
                        </h2>


                        <p>
                            Email:
                            {" "}
                            {customer.email}
                        </p>



                        <p>

                            Status:

                            {" "}

                            <span
                            className={
                                customer.status === "Frozen"
                                ?
                                "frozen"
                                :
                                "active"
                            }
                            >

                            {customer.status}

                            </span>

                        </p>



                        {
                        customer.status === "Frozen"

                        ?

                        <button
                        onClick={
                            ()=>unfreezeCustomer(customer.id)
                        }
                        >

                            Unfreeze

                        </button>


                        :


                        <button
                        onClick={
                            ()=>freezeCustomer(customer.id)
                        }
                        >

                            Freeze

                        </button>

                        }



                        <button

                        onClick={
                            ()=>deleteCustomer(customer.id)
                        }

                        >

                            Delete

                        </button>


                    </div>


                ))

                }


            </div>


        </div>

    );


}


export default Customers;