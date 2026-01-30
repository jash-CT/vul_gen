package handlers

import (
	"context"
	"log"

	"google.golang.org/grpc"
)

func UnaryServerInterceptor() grpc.UnaryServerInterceptor {
	return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
		// Basic logging and error handling
		log.Printf("Handling gRPC method: %s", info.FullMethod)
		
		resp, err := handler(ctx, req)
		if err != nil {
			log.Printf("Error in method %s: %v", info.FullMethod, err)
		}

		return resp, err
	}
}