import os
import sys
import numpy as np
from src import logging
from sklearn.pipeline import Pipeline
from src.exception import CustomException
from sklearn.compose import ColumnTransformer
from src.entity import DataTransformationConfig
from sklearn.model_selection import train_test_split
from src.utils import load_csv,read_yaml,save_numpy_array_data,save_object
from sklearn.preprocessing import StandardScaler,FunctionTransformer,OneHotEncoder

class DataTransformation:

    def __init__(self,data_transformation_config):

        self.datatransformation_config = data_transformation_config
        self.schema=read_yaml(self.datatransformation_config.yaml_file_path)

    def imputer(self,data,column):

        try:
            medians = data[data[column].notnull()].groupby('City').apply(lambda x: (x['Super Built-Up Area'] / x[column]).median())
            for idx in data[data[column].isnull()].index:
                city = data.loc[idx, 'City']
                area = data.loc[idx, 'Super Built-Up Area']
                estimated_value = (2 * area // medians[city]) // 2
                data.loc[idx, column] = estimated_value
            return data
        except Exception as e:
            raise CustomException(e,sys)
        
    def split_data(self,data):

        try:
            target=list(self.schema['target'].keys())[0]
            X = data.drop(target, axis=1)
            y = data[[target]]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.datatransformation_config.train_test_split_ratio, random_state=42)
            logging.info("Data Split successful")
            return X_train, X_test, y_train, y_test
        except Exception as e:
            raise CustomException(e,sys)

    def handle_null_values(self,data):

        try:
            for columns in data.columns:
                data[columns]=data[columns].replace('"NaN"',np.nan)
            data["Furnishing State"]=data["Furnishing State"].fillna("Not Specified")
            data["Flooring type"]=data["Flooring type"].fillna("Not Specified")
            data["Direction facing"]=data["Direction facing"].fillna("Not Specified")
            data["Property on"]=data["Property on"].fillna("Not Specified")
            data["Servant Accomation"]=data["Servant Accomation"].fillna("Not Specified")
            data["Brokerage terms"]=data["Brokerage terms"].fillna("No")
            data["Non Vegetarian"]=data["Non Vegetarian"].fillna(data["Non Vegetarian"].mode()[0])
            data["Pet Allowed"]=data["Pet Allowed"].fillna(data["Pet Allowed"].mode()[0])
            data.drop("Year of Construction",axis=1,inplace=True)
            logging.info("Null Values handled for categorical variables")

            data=self.imputer(data,"Bathrooms")
            data=self.imputer(data,"Bedrooms")
            data['Security Deposit']=data['Security Deposit'].fillna(data.groupby('City')['Security Deposit'].transform('mean'))
            data.dropna(subset=["Rent"], inplace=True)
            logging.info("Null Values handled for Numerical variables")

            return data

        except Exception as e:
            raise CustomException(e,sys) 
        
    def detect_outliers(self,data,feature):

        try:
            outliers = []
            data = sorted(data[feature])
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            IQR = q3-q1
            lwr_bound = q1-(1.5*IQR)
            upr_bound = q3+(1.5*IQR)
            for i in data: 
                if (i<lwr_bound or i>upr_bound):
                    outliers.append(i)
            return outliers
        except Exception as e:
            raise CustomException(e,sys) 
        
    def handle_outliers(self,data,features):

        try:
            for feature in features:
                if len(self.detect_outliers(data,feature))!=0:
                    data[feature]=np.clip(data[feature],np.percentile(data[feature], 10),np.percentile(data[feature], 90))
            return data
        except Exception as e:
            raise CustomException(e,sys)
        
    def get_feature_transformer(self,numerical_features,categorical_features):

        try:
            preprocessor = ColumnTransformer(transformers=[
            ('cat_transformer', OneHotEncoder(handle_unknown='ignore'),categorical_features),
            ('num_transformer', StandardScaler(),numerical_features),
            ])
            return preprocessor
        except Exception as e:
            raise CustomException(e,sys)
        
    def get_target_transformer(self):

        try:
            target_transformer=Pipeline(steps=[('skew_correction', FunctionTransformer(np.log1p,inverse_func=np.exp)),('skew_scaler', StandardScaler())])
            return target_transformer
        except Exception as e:
            raise CustomException(e,sys)
        
    def initiate_data_transformation(self):

        try:
            logging.info(">>>>>>>>> Data Transformation Stage Started")

            df=load_csv(self.datatransformation_config.validated_path)
            logging.info(f"Validated Data loaded successfully")
            df.drop_duplicates(inplace=True)
            df=self.handle_null_values(df)

            total_columns=[feature for feature in list(self.schema['features'].keys()) if feature in df.columns]
            logging.info(f"Total Columns :{total_columns}")
            numerical_features=[column for column in total_columns if df[column].dtype!='O']
            logging.info(f"Numerical features :{numerical_features}")
            categorical_features=[column for column in total_columns if df[column].dtype=='O']
            logging.info(f"Categorical features :{categorical_features}")

            df=self.handle_outliers(df,numerical_features)

            X_train, X_test, y_train, y_test=self.split_data(df)

            target_transformer=self.get_target_transformer()
            feature_transformer=self.get_feature_transformer(numerical_features,categorical_features)
            logging.info(f"Target and Feature Transformer retrieved Successfully")

            X_train_transformed=feature_transformer.fit_transform(X_train).toarray()
            X_test_transformed=feature_transformer.transform(X_test).toarray()
            logging.info(f"Independent Features Transformed Successfully")
            
            Y_train_transformed=target_transformer.fit_transform(y_train)
            Y_test_transformed=target_transformer.transform(y_test)
            logging.info(f"Dependent Features Transformed Successfully")

            train_arr = np.c_[X_train_transformed, Y_train_transformed]
            test_arr = np.c_[X_test_transformed, Y_test_transformed]

            save_numpy_array_data(train_arr,self.datatransformation_config.train_path)
            logging.info(f"Train Data Saved at {self.datatransformation_config.train_path}")

            save_numpy_array_data(test_arr,self.datatransformation_config.test_path)
            logging.info(f"Test Data Saved at {self.datatransformation_config.test_path}")

            save_object(target_transformer,self.datatransformation_config.target_transformer_path)
            logging.info(f"Target Transformer Saved at {self.datatransformation_config.target_transformer_path}")

            save_object(feature_transformer,self.datatransformation_config.feature_transformer_path)
            logging.info(f"Feature Transformer Saved at {self.datatransformation_config.feature_transformer_path}")

            logging.info("Data Transformation completed <<<<<<<<<")

        except Exception as e:
            raise CustomException(e,sys)
        
if __name__ == "__main__":

    obj=DataTransformation(DataTransformationConfig())
    obj.initiate_data_transformation()