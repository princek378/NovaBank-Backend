import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function NewCustomer() {

    const navigate = useNavigate();

    const [form, setForm] = useState({
        first_name: "",
        last_name: "",
        email: "",
        password: "",
        phone: "",
        country: "",
        address: "",
        account_type: "Savings",
        balance: 0
    });

    function handleChange(e) {

        setForm({
            ...form,
            [e.target.name]: e.target.value
        });

    }

    async function handleSubmit(e) {

        e.preventDefault();

        const response = await fetch(
            "http://127.0.0.1:5000/api/admin/customers",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(form)
            }
        );

        const data = await response.json();

        if (response.ok) {

            alert(
                "Customer created!\n\nAccount Number: " +
                data.account_number
            );

            navigate("/admin/customers");

        } else {

            alert(data.message);

        }

    }

    return (

        <div className="new-customer-page">

            <h1>Create New Customer</h1>

            <form
                className="customer-form"
                onSubmit={handleSubmit}
            >

                <input
                    name="first_name"
                    placeholder="First Name"
                    onChange={handleChange}
                    required
                />

                <input
                    name="last_name"
                    placeholder="Last Name"
                    onChange={handleChange}
                    required
                />

                <input
                    name="email"
                    type="email"
                    placeholder="Email"
                    onChange={handleChange}
                    required
                />

                <input
                    name="password"
                    type="password"
                    placeholder="Password"
                    onChange={handleChange}
                    required
                />

                <input
                    name="phone"
                    placeholder="Phone"
                    onChange={handleChange}
                />

                <input
                    name="country"
                    placeholder="Country"
                    onChange={handleChange}
                />

                <input
                    name="address"
                    placeholder="Address"
                    onChange={handleChange}
                />

                <select
                    name="account_type"
                    onChange={handleChange}
                >
                    <option>Savings</option>
                    <option>Current</option>
                    <option>Business</option>
                </select>

                <input
                    name="balance"
                    type="number"
                    placeholder="Opening Balance"
                    onChange={handleChange}
                />

                <button type="submit">
                    Create Customer
                </button>

            </form>

        </div>

    );

}