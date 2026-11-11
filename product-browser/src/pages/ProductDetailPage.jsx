import { useState } from "react";
import { useEffect } from "react";
import { useParams } from 'react-router'
import { Link } from "react-router";

function ProductDetailPage() {
    const { id } = useParams();
    const [product, setProduct] = useState(null);

    useEffect(() => {
        async function loadProduct() {
            const res = await fetch(`https://dummyjson.com/products/${id}`);
            const data = await res.json();
            setProduct(data);
        }
        loadProduct();
    }, [id]);

    if (!product) {
        return <p>Loading...</p>;
    }

    return (
        <>
        <Link to="/">Back to Products</Link>
        <h2>{product.title}</h2>
        <p><strong>Description:</strong> {product.description}</p>
        <p><strong>Price:</strong> ${product.price}</p>
        <p><strong>Rating:</strong> {product.rating}</p>
        <p><strong>Category:</strong> {product.category}</p>
        <p><strong>Stock:</strong> {product.stock}</p>
        <h3>Images:</h3>
            {product.images.map((image, index) => (
                <img key={index} src={image} width="150" />
            ))}
        <h3>Reviews:</h3>
        <ul>
            {product.reviews.map((review) => (
                <li key={review.reviewerEmail}>
                    {review.reviewerName} ({review.rating}/5): {review.comment}
                </li>
            ))}
        </ul>
        </>               
    );
}

export default ProductDetailPage