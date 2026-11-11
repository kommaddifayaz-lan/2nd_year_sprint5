import { useState } from "react";
import { useEffect } from "react";
import { Link } from "react-router";

function ProductsPage() {
    const[products, setProducts] = useState([]);
 
    useEffect(() => {
        async function loadProducts() {
            const res = await fetch("https://dummyjson.com/products");
            const data = await res.json();
            
            setProducts(data.products);
        }
        loadProducts();
    }, []);

    return(
        <>
        <p>Loaded {products.length} products</p>
        <ol>
            {products.map((product) => (
                <li key={product.id}>
                    <img src={product.thumbnail}></img>
                    <h2>{product.title}</h2>
                    <p><strong>Price:</strong> ${product.price}</p>
                    <p><strong>Rating:</strong> {product.rating}</p>
                    <p><strong>Category:</strong> {product.category}</p>
                    <p><strong>Reviews:</strong> {product.reviews.length}</p>
                    <Link to={`/products/${product.id}`}>View Details</Link>
                
                </li>

            ))}
        </ol>
        </>
    )

}

export default ProductsPage;