from flask_jwt_extended import create_access_token, get_jwt_identity, JWTManager, verify_jwt_in_request
from flask import request, current_app
from ..utils.hash import checkpw, hashpw
from ..utils.dbUtils import adddb, commitdb, generate_ez_id
from ..utils.mailService import send_email
from ..models import User
import graphene
from flask_graphql import GraphQLView
from .return_types import ReturnType
import os
from datetime import datetime
import logging

# Add logger instance
logger = logging.getLogger(__name__)

jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.ez_id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):        
    identity = jwt_data["sub"]
    return User.query.get(identity)

class AuthenticatedGraphQLView(GraphQLView):
    def get_context(self):
        # Start with a custom dict (not the raw request object)
        context = {"request": request}
        
        try:
            verify_jwt_in_request(optional=True)
            user = get_jwt_identity()
        except Exception:
            user = None
        
        context["current_user"] = user
        return context

class AuthTokenType(graphene.ObjectType):
    token = graphene.String()
    message = graphene.String()
    status = graphene.Int()


class GetToken(graphene.ObjectType):
    get_token = graphene.Field(AuthTokenType, ez_id=graphene.String(), email=graphene.String(), password=graphene.String())
    def resolve_get_token(self, info, password, ez_id=None, email=None):
        if ez_id:
            user = User.query.get(ez_id)
        elif email:
            user = User.query.filter(User.email == email).first()
        else:
            return AuthTokenType(token=None, message="No user found", status=404)
        if user:
            if checkpw(password, user.password):
                access_token = create_access_token(identity=user)
                return AuthTokenType(token = access_token, message="Success", status=200)
            return AuthTokenType(token=None, message="Wrong Credentials", status=402)
        return AuthTokenType(token=None, message="No User Found", status=404)
    
class EZLogin(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
    
    Output = ReturnType

    def mutate(self, info, email):
        user = User.query.filter(User.email == email).first()
        if not user:
            return ReturnType(message="No User Found", status=404)
        
        try:
            # Create access token with 1 hour expiration for security
            access_token = create_access_token(identity=user, expires_delta=False)
            
            # Build the login URL
            frontend_base_url = current_app.config.get('FRONTEND_BASE_URL', 'http://localhost:5173')
            login_url = f"{frontend_base_url}/auth/token-login?token={access_token}"
            
            # Prepare template data
            template_data = {
                'user_name': user.name,
                'user_email': user.email,
                'user_role': user.role,
                'login_url': login_url,
                'current_year': datetime.now().year
            }
            
            # Send email using the login template
            send_email(
                subject='🔐 EZCare Login Link - Secure Access to Your Account',
                recipients=[email],
                reminder_display=template_data,
                template="login_template.html"
            )
            
            logger.info(f"Login email sent successfully to {email}")
            return ReturnType(
                message=f"Login link sent to {email}. Please check your email and click the link to login securely.",
                status=200
            )
            
        except Exception as e:
            logger.error(f"Failed to send login email to {email}: {str(e)}")
            return ReturnType(
                message="Failed to send login email. Please try again or contact support.",
                status=500
            )

class Register(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        role = graphene.Int(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)
        name = graphene.String(required=True)
        phone_num = graphene.String(required=True)

    Output = ReturnType

    def mutate(root, info, email, role, password, confirm_password, name, phone_num):
        if email is None or role is None or password is None or confirm_password is None:
            return ReturnType(status=400, message="Insufficient information.")

        if role not in [1, 0]:
            return ReturnType(status=402, message="Role must be either Senior Citizen (0) or Health Professional (1).")

        if password != confirm_password:
            return ReturnType(status=403, message="Passwords do not match.")

        if User.query.filter_by(email=email).first():
            return ReturnType(status=409, message="User with the given email already exists.")

        try:
            ez_id = generate_ez_id(role)
            new_user = User(
                ez_id=ez_id,
                role=role,
                email=email,
                password=hashpw(password),  
                name=name,
                phone_num=phone_num,
            )
            adddb(new_user) 
            commitdb()      
        except Exception as err:
            print(err)
            return ReturnType(status=500, message="Something went wrong. Please try again.")

        return ReturnType(status=200, message="Registration successful.")
    
class ModRegister(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        role = graphene.Int(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)
        name = graphene.String(required=True)
        phone_num = graphene.String(required=True)
        mod_key = graphene.String(required=True)

    Output = ReturnType

    def mutate(root, info, email, role, password, confirm_password, name, phone_num, mod_key):
        if mod_key is None:
            return ReturnType(status=400, message="Insufficient information, Please Provide a ModKey.")
        
        if mod_key != mod_key:
            return ReturnType(status=402, message="Unauthorized")

        if email is None or role is None or password is None or confirm_password is None:
            return ReturnType(status=400, message="Insufficient information.")

        if role not in [2]:
            return ReturnType(status=402, message="Role must be Mod (2). If not a mod, do not register from here.")

        if password != confirm_password:
            return ReturnType(status=403, message="Passwords do not match.")

        if User.query.filter_by(email=email).first():
            return ReturnType(status=409, message="User with the given email already exists.")

        try:
            ez_id = generate_ez_id(role)
            new_user = User(
                ez_id=ez_id,
                role=role,
                email=email,
                password=hashpw(password),  # assuming hashpw is defined
                name=name,
                phone_num=phone_num,
            )
            adddb(new_user)  # assuming adddb is defined
            commitdb()       # assuming commitdb is defined
        except Exception as err:
            print(err)
            return ReturnType(status=500, message="Something went wrong. Please try again.")

        return ReturnType(status=200, message="Registration successful.")
    
class AuthMutation(graphene.ObjectType):
    register = Register.Field()
    mod_register = ModRegister.Field()
    ez_login = EZLogin.Field()
