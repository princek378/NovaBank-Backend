import "./TransactionReceipt.css";

export default function TransactionReceipt({transaction}) {
 if(!transaction) return null;

 return (
  <div className="receipt">
   <h2>NovaBank Receipt</h2>
   <p>Reference: {transaction.reference}</p>
   <p>Description: {transaction.description}</p>
   <p>Type: {transaction.type}</p>
   <p>Amount: {'$' + Number(transaction.amount).toFixed(2)}</p>
   <p>Status: {transaction.status}</p>
   <p>Date: {new Date(transaction.date).toLocaleString()}</p>
  </div>
 );
}
