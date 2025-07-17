from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from store.models import Product
from .models import Review
from .forms import ReviewForm

#Add review by id
@login_required
def add_review(request, product_id):
    try:
        product_id = int(product_id)
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check if user already reviewed this product
        existing_review = Review.objects.filter(product=product, user=request.user).first()
        
        if request.method == 'POST':
            if existing_review:
                # Update existing review
                form = ReviewForm(request.POST, instance=existing_review)
                action = 'updated'
            else:
                # Create new review
                form = ReviewForm(request.POST)
                action = 'added'
            
            if form.is_valid():
                try:
                    review = form.save(commit=False)
                    review.product = product
                    review.user = request.user
                    review.save()
                    messages.success(request, f'Your review has been {action} successfully!')
                    return redirect('store:product_detail', pk=product.pk)
                except Exception:
                    messages.error(request, 'Unable to save review. Please try again.')
        else:
            form = ReviewForm(instance=existing_review) if existing_review else ReviewForm()
        
        return render(request, 'reviews/add_review.html', {
            'form': form,
            'product': product,
            'existing_review': existing_review
        })
    except (ValueError, TypeError):
        messages.error(request, 'Invalid product.')
        return redirect('store:product_list')


# Delete review by review id
@login_required
def delete_review(request, review_id):
    try:
        review_id = int(review_id)
        review = get_object_or_404(Review, id=review_id, user=request.user)
        
        if request.method == 'POST':
            try:
                product_pk = review.product.pk
                review.delete()
                messages.success(request, 'Your review has been deleted.')
                return redirect('store:product_detail', pk=product_pk)
            except Exception:
                messages.error(request, 'Unable to delete review. Please try again.')
        
        return render(request, 'reviews/delete_review.html', {'review': review})
    except (ValueError, TypeError):
        messages.error(request, 'Invalid review.')
        return redirect('store:product_list')

#Return the reviews for product
def get_product_reviews(product, limit=6):
    try:
        reviews = Review.objects.filter(product=product).select_related('user')
        if limit:
            reviews = reviews[:limit]
        return reviews
    except Exception:
        return Review.objects.none()

# Get rating statistics for product (average, total reviews, distribution of ratings)
def get_product_rating_stats(product):
    try:
        reviews = Review.objects.filter(product=product)
        if not reviews.exists():
            return {
                'average_rating': 0,
                'total_reviews': 0,
                'rating_distribution': {i: 0 for i in range(1, 6)}
            }
        
        total_reviews = reviews.count()
        total_rating = sum(review.rating for review in reviews)
        average_rating = round(total_rating / total_reviews, 1)
        
        # Rating distribution
        rating_distribution = {i: 0 for i in range(1, 6)}
        for review in reviews:
            rating_distribution[review.rating] += 1
        
        return {
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'rating_distribution': rating_distribution
        }
    except Exception:
        return {
            'average_rating': 0,
            'total_reviews': 0,
            'rating_distribution': {i: 0 for i in range(1, 6)}
        }