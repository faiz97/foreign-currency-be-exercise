from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min
from django.shortcuts import render
from currencies.models import Currency, CurrencyRate
from currencies.serializers import CurrencySerializer, CurrencyRateSerializer, CurrencyRateCreatorRequestSerializer
from rest_framework import status as st
from rest_framework import exceptions
from rest_framework import generics
from rest_framework.response import Response
import re

# Create your views here.
class CurrencyCreator(generics.CreateAPIView):
    serializer_class = CurrencySerializer

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        If `request.method` does not correspond to a handler method,
        determine what kind of exception to raise.
        """
        try:
            raise exceptions.MethodNotAllowed(request.method)
        except exceptions.MethodNotAllowed as exc:
            details = exc.detail
            stat = exc.status_code
            res = {'status': stat, 'message': 'Method Not Allowed', 'details': details}
            return Response(res, status=stat)
        
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            stat = st.HTTP_201_CREATED
            res = {'status': stat, 'message': 'Created'}
            res.update(serializer.data)
            return Response(res, status=stat, headers=headers)
        except (exceptions.ValidationError, exceptions.ParseError) as exc:
            details = exc.detail
            status = exc.status_code
            res = {'status': status, 'message': 'Bad Request', 'details': details}
            return Response(res, status=status)
        except Exception as exc:
            details = []
            stat = st.HTTP_500_INTERNAL_SERVER_ERROR
            res = {'status': stat, 'message': 'Internal Server Error', 'details': details}
            return Response(res, status=stat)
       
class CurrencyList(generics.ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        If `request.method` does not correspond to a handler method,
        determine what kind of exception to raise.
        """
        try:
            raise exceptions.MethodNotAllowed(request.method)
        except exceptions.MethodNotAllowed as exc:
            details = exc.detail
            stat = exc.status_code
            res = {'status': stat, 'message': 'Method Not Allowed', 'details': details}
            return Response(res, status=stat)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            stat = st.HTTP_200_OK
            res = {'status': stat, 'message': 'OK'}
            res.update({'currencies': serializer.data})
            return Response(res, status=stat)
        except Exception as exc:
            details = []
            stat = st.HTTP_500_INTERNAL_SERVER_ERROR
            res = {'status': stat, 'message': 'Internal Server Error', 'details': details}
            return Response(res, status=stat)


class CurrencyDestroyer(generics.DestroyAPIView):
    serializer_class = CurrencySerializer

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        If `request.method` does not correspond to a handler method,
        determine what kind of exception to raise.
        """
        try:
            raise exceptions.MethodNotAllowed(request.method)
        except exceptions.MethodNotAllowed as exc:
            details = exc.detail
            stat = exc.status_code
            res = {'status': stat, 'message': 'Method Not Allowed', 'details': details}
            return Response(res, status=stat)
    
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `currency_id` query parameter in the URL.
        """
        queryset = Currency.objects.all()
        currency_id = self.request.query_params.get('currency_id', None)
        if currency_id is not None:
            queryset = queryset.filter(currency_id=currency_id)
        return queryset

    def destroy(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(self.get_queryset().first())
            instance = self.get_queryset().first()

            if instance is None:
                raise exceptions.NotFound

            self.perform_destroy(instance)
            stat = st.HTTP_204_NO_CONTENT
            res = {'status': stat, 'message': 'No Content'}
            res.update(serializer.data)
            return Response(res, status=stat)
        except (exceptions.ValidationError, exceptions.ParseError) as exc:
            details = exc.detail
            status = exc.status_code
            res = {'status': status, 'message': 'Bad Request', 'details': details}
            return Response(res, status=status)
        except exceptions.NotFound as exc:
            details = exc.detail
            status = exc.status_code
            res = {'status': status, 'message': 'Not Found', 'details': details}
            return Response(res, status=status)
        except Exception as exc:
            details = []
            stat = st.HTTP_500_INTERNAL_SERVER_ERROR
            res = {'status': stat, 'message': 'Internal Server Error', 'details': details}
            return Response(res, status=stat)


class CurrencyDateList(generics.ListAPIView):
    serializer_class = CurrencyRateSerializer

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        If `request.method` does not correspond to a handler method,
        determine what kind of exception to raise.
        """
        try:
            raise exceptions.MethodNotAllowed(request.method)
        except exceptions.MethodNotAllowed as exc:
            details = exc.detail
            stat = exc.status_code
            res = {'status': stat, 'message': 'Method Not Allowed', 'details': details}
            return Response(res, status=stat)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `date` query parameter in the URL.
        """
        queryset = CurrencyRate.objects.all()
        date = self.request.query_params.get('date', None)

        if not re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', date):
            raise exceptions.ParseError

        if date is not None:
            queryset = queryset.filter(date=date)
            currency_rate_serializer_list = [CurrencyRateSerializer(obj) for obj in queryset]
            currency_id_list = [obj.data['currency_id'] for obj in currency_rate_serializer_list]
            queryset = Currency.objects.all()
            queryset = queryset.filter(currency_id__in=currency_id_list)
        else:
            raise exceptions.ParseError

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            currency_serializer_list = [CurrencySerializer(obj) for obj in queryset]
            currency_id_domain_codomain_list = \
                [{ 'currency_id': obj.data['currency_id'],'domain': obj.data['domain'], 'codomain': obj.data['codomain']} \
                    for obj in currency_serializer_list]
            rows = []

            date = self.request.query_params.get('date', None)
            format_str = '%Y-%m-%d' # The format
            datetime_obj = datetime.strptime(date, format_str)

            for obj in currency_id_domain_codomain_list:
                currency_id = obj['currency_id']
                domain = obj['domain']
                codomain = obj['codomain']
                queryset = last_seven_days_rates(domain, codomain, date=datetime_obj)
                rate = CurrencyRateSerializer(queryset.filter(currency_id=currency_id, date=datetime.now()).first()).data['rate']
                average = queryset.aggregate(Avg('rate'))['rate__avg']
                rows.append({'currency_id': currency_id, 'domain': domain, 'codomain': codomain, 'rate': rate, 'average': average})

            serializer = self.get_serializer(queryset, many=True)
            stat = st.HTTP_200_OK
            res = {'status': stat, 'date': date, 'message': 'OK', 'rows': rows}
            return Response(res, status=stat)
        except (exceptions.ValidationError, exceptions.ParseError) as exc:
            details = exc.detail
            status = exc.status_code
            res = {'status': status, 'message': 'Bad Request', 'details': details}
            return Response(res, status=status)
        except exceptions.NotFound as exc:
            details = exc.detail
            status = exc.status_code
            res = {'status': status, 'message': 'Not Found', 'details': details}
            return Response(res, status=status)
        except Exception as exc:
            details = []
            stat = st.HTTP_500_INTERNAL_SERVER_ERROR
            res = {'status': stat, 'message': 'Internal Server Error', 'details': details}
            return Response(res, status=stat)


class CurrencyRateCreator(generics.CreateAPIView):
    serializer_class = CurrencyRateCreatorRequestSerializer

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        If `request.method` does not correspond to a handler method,
        determine what kind of exception to raise.
        """
        try:
            raise exceptions.MethodNotAllowed(request.method)
        except exceptions.MethodNotAllowed as exc:
            details = exc.detail
            stat = exc.status_code
            res = {'status': stat, 'message': 'Method Not Allowed', 'details': details}
            return Response(res, status=stat)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            domain = serializer.data['domain']
            codomain = serializer.data['codomain']
            date = serializer.data['date']
            rate = serializer.data['rate']
            currency_query_result = Currency.objects.filter(domain=domain, codomain=codomain).first()
            currency_rate_serializer_data = {}

            if currency_query_result is None:
                currency_rate_serializer_data = self._insert_currency_and_rate(domain=domain, codomain=codomain, date=date, rate=rate)
            else:
                currency_id = CurrencySerializer(currency_query_result).data['currency_id']
                currency_rate_serializer_data = self._insert_rate(currency_id=currency_id, date=date, rate=rate)

            stat = st.HTTP_201_CREATED
            res = {'status': stat, 'message': 'Created'}
            res.update(currency_rate_serializer_data)
            return Response(res, status=stat)
        except (exceptions.ValidationError, exceptions.ParseError) as exc:
            details = exc.detail
            status = exc.status_code
            res = {'status': status, 'message': 'Bad Request', 'details': details}
            return Response(res, status=status)
        except Exception as exc:
            details = []
            stat = st.HTTP_500_INTERNAL_SERVER_ERROR
            res = {'status': stat, 'message': 'Internal Server Error', 'details': details}
            return Response(res, status=stat)

    def _insert_currency_and_rate(self, domain, codomain, date, rate):
        currency_data = {'domain': domain, 'codomain': codomain}
        currency_serializer = CurrencySerializer(data=currency_data)
        currency_serializer.is_valid(raise_exception=True)
        currency_serializer.save()

        currency_id = currency_serializer.data['currency_id']
        currency_rate_data = {'currency_id': currency_id, 'rate': rate, 'date': date}
        currency_rate_serializer = CurrencyRateSerializer(data=currency_rate_data)
        currency_rate_serializer.is_valid(raise_exception=True)
        currency_rate_serializer.save()

        return currency_rate_serializer.data

    def _insert_rate(self, currency_id, date, rate):
        rate_query_result = CurrencyRate.objects.filter(currency_id=currency_id, date=date).first()
        currency_rate_data = {'currency_id': currency_id, 'rate': rate, 'date': date}
        currency_rate_serializer = {'data': ''}

        if rate_query_result is None:
            currency_rate_serializer = CurrencyRateSerializer(data=currency_rate_data)
            currency_rate_serializer.is_valid(raise_exception=True)
            currency_rate_serializer.save()
        else:
            rate_query_result = CurrencyRate.objects.get(currency_id=currency_id, date=date)
            rate_query_result.update(rate=rate)
            new_rate_query_result = CurrencyRate.objects.get(currency_id=currency_id, date=date)
            currency_rate_serializer = CurrencyRateSerializer(new_rate_query_result)

        return currency_rate_serializer.data


class CurrencyRatesTrendList(generics.ListAPIView):
    serializer_class = CurrencyRateSerializer

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        If `request.method` does not correspond to a handler method,
        determine what kind of exception to raise.
        """
        try:
            raise exceptions.MethodNotAllowed(request.method)
        except exceptions.MethodNotAllowed as exc:
            details = exc.detail
            stat = exc.status_code
            res = {'status': stat, 'message': 'Method Not Allowed', 'details': details}
            return Response(res, status=stat)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `domain` and  `codomain` query parameter in the URL.
        """
        domain = self.request.query_params.get('domain', None)
        codomain = self.request.query_params.get('codomain', None)
        queryset = last_seven_days_rates(domain=domain, codomain=codomain)
        
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            domain = self.request.query_params.get('domain', None)
            codomain = self.request.query_params.get('codomain', None)
            average = queryset.aggregate(Avg('rate'))['rate__avg']
            variance = queryset.aggregate(Max('rate'))['rate__max'] - queryset.aggregate(Min('rate'))['rate__min']

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            stat = st.HTTP_200_OK
            res = {'status': stat, 'message': 'OK', 'domain': domain, 'codomain': codomain, 'average': average, 'variance': variance}
            res.update({'rates': serializer.data})
            return Response(res, status=stat)
        except (exceptions.ValidationError, exceptions.ParseError) as exc:
            details = exc.detail
            status = exc.status_code
            res = {'status': status, 'message': 'Bad Request', 'details': details}
            return Response(res, status=status)
        except exceptions.NotFound as exc:
            details = exc.detail
            status = exc.status_code
            res = {'status': status, 'message': 'Not Found', 'details': details}
            return Response(res, status=status)
        except Exception as exc:
            details = []
            stat = st.HTTP_500_INTERNAL_SERVER_ERROR
            res = {'status': stat, 'message': 'Internal Server Error', 'details': details}
            return Response(res, status=stat)

def last_seven_days_rates(domain, codomain, date=None):
    if domain is None or codomain is None:
        raise exceptions.ParseError

    queryset = Currency.objects.all()
    queryset = queryset.filter(domain=domain, codomain=codomain)

    if queryset.first() is None:
        raise exceptions.NotFound

    currency_id = CurrencySerializer(queryset.first()).data['currency_id']
    queryset = CurrencyRate.objects.all()
    how_many_days = 7

    if date is None:
        date = datetime.now()

    queryset = queryset.filter(currency_id=currency_id)
    queryset = queryset.filter(date__gt=date-timedelta(days=how_many_days))

    return queryset
