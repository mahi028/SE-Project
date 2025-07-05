export const reviewService = {
    getReviews() {
        return [
            {
                "review_id": "R001",
                "sen_id": "S001",
                "doc_id": "D001",
                "rating": 5,
                "review": "Dr. Rajesh is an excellent cardiologist. Very thorough in his examination and explains everything clearly. Highly recommend!"
            },
            {
                "review_id": "R002",
                "sen_id": "S002",
                "doc_id": "D001",
                "rating": 4,
                "review": "Good doctor, but the waiting time was quite long. Overall satisfied with the treatment."
            },
            {
                "review_id": "R003",
                "sen_id": "S003",
                "doc_id": "D002",
                "rating": 5,
                "review": "Dr. Priya is amazing! She took great care of my diabetes management. Very caring and professional."
            },
            {
                "review_id": "R004",
                "sen_id": "S004",
                "doc_id": "D002",
                "rating": 5,
                "review": "Excellent endocrinologist. My blood sugar levels have improved significantly under her care."
            },
            {
                "review_id": "R005",
                "sen_id": "S005",
                "doc_id": "D003",
                "rating": 4,
                "review": "Dr. Amit performed my surgery successfully. Recovery was smooth. Thank you doctor!"
            },
            {
                "review_id": "R006",
                "sen_id": "S001",
                "doc_id": "D004",
                "rating": 5,
                "review": "Dr. Sunita is very knowledgeable about neurology. She helped me with my migraine issues effectively."
            },
            {
                "review_id": "R007",
                "sen_id": "S006",
                "doc_id": "D005",
                "rating": 3,
                "review": "Decent consultation but felt rushed. Could have spent more time explaining the condition."
            },
            {
                "review_id": "R008",
                "sen_id": "S007",
                "doc_id": "D006",
                "rating": 5,
                "review": "Dr. Kavita is the best dermatologist I've visited. My skin condition improved dramatically."
            },
            {
                "review_id": "R009",
                "sen_id": "S008",
                "doc_id": "D007",
                "rating": 4,
                "review": "Good urologist. Professional approach and effective treatment. Would recommend."
            },
            {
                "review_id": "R010",
                "sen_id": "S009",
                "doc_id": "D008",
                "rating": 5,
                "review": "Dr. Meera is excellent with pediatric care. My grandchild feels comfortable with her."
            },
            {
                "review_id": "R011",
                "sen_id": "S010",
                "doc_id": "D009",
                "rating": 4,
                "review": "Great psychiatrist. Helped me deal with anxiety issues. Very understanding and patient."
            },
            {
                "review_id": "R012",
                "sen_id": "S002",
                "doc_id": "D010",
                "rating": 5,
                "review": "Dr. Pooja's eye treatment was excellent. My vision has improved significantly."
            },
            {
                "review_id": "R013",
                "sen_id": "S003",
                "doc_id": "D001",
                "rating": 4,
                "review": "Very experienced cardiologist. Explains procedures well and makes you feel at ease."
            },
            {
                "review_id": "R014",
                "sen_id": "S005",
                "doc_id": "D002",
                "rating": 5,
                "review": "Outstanding care from Dr. Priya. She's very thorough and genuinely cares about patients."
            },
            {
                "review_id": "R015",
                "sen_id": "S008",
                "doc_id": "D003",
                "rating": 4,
                "review": "Successful surgery by Dr. Amit. Professional team and good post-operative care."
            }
        ];
    },

    getReviewsByDoctor(doctorId) {
        return Promise.resolve(
            this.getReviews().filter(review => review.doc_id === doctorId)
        );
    },

    getAverageRating(doctorId) {
        const reviews = this.getReviews().filter(review => review.doc_id === doctorId);
        if (reviews.length === 0) return 0;
        const total = reviews.reduce((sum, review) => sum + review.rating, 0);
        return (total / reviews.length).toFixed(1);
    },

    getReviewCount(doctorId) {
        return this.getReviews().filter(review => review.doc_id === doctorId).length;
    }
};
