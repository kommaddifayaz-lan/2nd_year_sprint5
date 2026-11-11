import { useState } from 'react';
import { useEffect } from "react";
import { Link } from "react-router";

function BrowsePage() {
    const [products, setProducts] = useState([]);
    const [page, setPage] = useState(1);   

    useEffect(() => {
        async function loadProducts() {
            const skip = (page - 1) * 10;
            const res = await fetch(`https://dummyjson.com/products?limit=10&skip=${skip}`);
            const data = await res.json();
            setProducts(data.products);
        }
        loadProducts();
    }, [page]);

    return (
        <>
        <button disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button>
        <span>Page {page}</span>
        <button onClick={() => setPage(page + 1)}>Next</button>
        <p>Loaded {products.length} products</p>
        <ul>
            {products.map((product) => (
                <li key={product.id}>
                    <img src={product.thumbnail} alt={product.title} />
                    <h2>{product.title}</h2>
                    <p><strong>Price:</strong> ${product.price}</p>
                    <p><strong>Rating:</strong> {product.rating}</p> 
                    <p><strong>Category:</strong> {product.category}</p>
                    <p><strong>Reviews:</strong> {product.reviews.length}</p>
                    <Link to={`/products/${product.id}`}>View Details</Link>
                </li>
            ))}
        </ul>
        </>
    );
}

export default BrowsePage;